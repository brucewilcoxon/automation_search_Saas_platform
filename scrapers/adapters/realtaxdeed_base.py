"""
Base adapter for RealTaxDeed.com auction platforms.
Many Florida counties use this platform with similar structure.
"""
import re
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from scrapers.adapters.base import BaseCountyAdapter
import logging

logger = logging.getLogger(__name__)


class RealTaxDeedBaseAdapter(BaseCountyAdapter):
    """
    Base adapter for RealTaxDeed.com platform.
    Provides common functionality for counties using this platform.
    """
    
    def __init__(self, county_id: str, source_url: str, county_name: str):
        """
        Initialize the RealTaxDeed adapter.
        
        Args:
            county_id: County identifier
            source_url: Base URL for the auction source (e.g., https://miamidade.realforeclose.com)
            county_name: Display name of the county
        """
        super().__init__(county_id, source_url)
        self.county_name = county_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 1.0  # Minimum seconds between requests
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=1, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout)),
        reraise=True
    )
    def _make_request(self, url: str, timeout: int = 30) -> requests.Response:
        """Make HTTP request with rate limiting and retry."""
        self._rate_limit()
        logger.info(f"Making request to {url}")
        response = self.session.get(url, timeout=timeout)
        response.raise_for_status()
        return response
    
    def discover_auction_events(self) -> List[Dict[str, Any]]:
        """
        Discover auction events from RealTaxDeed platform.
        Typically found on the main auctions page.
        """
        events = []
        try:
            # Common pattern: /index.cfm?zaction=AUCTION&zmethod=CALENDAR
            calendar_url = f"{self.source_url}/index.cfm?zaction=AUCTION&zmethod=CALENDAR"
            response = self._make_request(calendar_url)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for auction event links/rows
            # Common patterns: table rows, divs with auction dates, links to auction pages
            event_rows = soup.find_all(['tr', 'div'], class_=re.compile(r'auction|event|sale', re.I))
            
            for row in event_rows:
                # Try to extract event date
                date_elem = row.find(string=re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'))
                if not date_elem:
                    date_elem = row.find(['span', 'td', 'div'], class_=re.compile(r'date', re.I))
                
                # Try to find event URL
                link = row.find('a', href=re.compile(r'auction|sale|event', re.I))
                
                if date_elem or link:
                    event_date_str = self._extract_date(date_elem)
                    event_url = self._extract_event_url(link, row)
                    
                    if event_date_str:
                        try:
                            event_date = self._parse_date(event_date_str)
                            event_id = self._generate_event_id(event_date)
                            
                            events.append({
                                'event_id': event_id,
                                'event_date': event_date.isoformat(),
                                'event_url': event_url or f"{self.source_url}/index.cfm?zaction=AUCTION&zmethod=PREVIEW",
                                'status': self._determine_status(event_date),
                                'raw_json': {
                                    'source_url': calendar_url,
                                    'scraped_at': datetime.utcnow().isoformat(),
                                    'county': self.county_name,
                                    'html_snippet': str(row)[:500] if row else None
                                }
                            })
                        except (ValueError, AttributeError):
                            continue
            
            # If no events found with pattern matching, return at least one default event
            if not events:
                # Try to find any auction-related page
                events.append({
                    'event_id': f"{self.county_id}-default",
                    'event_date': date.today().isoformat(),
                    'event_url': f"{self.source_url}/index.cfm?zaction=AUCTION&zmethod=PREVIEW",
                    'status': 'upcoming',
                    'raw_json': {
                        'source_url': calendar_url,
                        'scraped_at': datetime.utcnow().isoformat(),
                        'county': self.county_name,
                        'note': 'Default event - pattern matching failed'
                    }
                })
                
        except Exception as e:
            # Return error in raw_json for debugging
            events.append({
                'event_id': f"{self.county_id}-error",
                'event_date': date.today().isoformat(),
                'event_url': self.source_url,
                'status': 'upcoming',
                'raw_json': {
                    'error': str(e),
                    'scraped_at': datetime.utcnow().isoformat()
                }
            })
        
        return events
    
    def list_auction_items(self, event_url: str) -> List[Dict[str, Any]]:
        """
        List auction items from an event page.
        """
        items = []
        try:
            response = self._make_request(event_url)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common patterns: table rows with item data, divs with item info
            item_rows = soup.find_all(['tr', 'div'], class_=re.compile(r'item|parcel|lot', re.I))
            
            # If no class-based matches, try finding tables
            if not item_rows:
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > 1:  # Has header + data rows
                        item_rows.extend(rows[1:])  # Skip header
            
            for row in item_rows:
                item_data = self._extract_item_data(row, event_url)
                if item_data:
                    items.append(item_data)
            
            # If no items found, return empty list (will be handled by caller)
            
        except Exception as e:
            # Log error but return empty list
            items.append({
                'item_id': f"error-{datetime.utcnow().timestamp()}",
                'parcel_id_raw': '',
                'opening_bid': None,
                'status': 'available',
                'item_url': event_url,
                'raw_json': {
                    'error': str(e),
                    'scraped_at': datetime.utcnow().isoformat()
                }
            })
        
        return items
    
    def normalize_parcel_id(self, raw_parcel_id: str) -> str:
        """
        Normalize parcel ID by removing common separators.
        RealTaxDeed typically uses formats like: 30-2104-001-0010
        """
        if not raw_parcel_id:
            return ""
        # Remove common separators: dashes, spaces, dots
        normalized = re.sub(r'[-.\s]', '', raw_parcel_id)
        return normalized.upper()
    
    def _extract_date(self, elem) -> Optional[str]:
        """Extract date string from element."""
        if not elem:
            return None
        if isinstance(elem, str):
            return elem.strip()
        text = elem.get_text() if hasattr(elem, 'get_text') else str(elem)
        # Look for date pattern
        match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
        return match.group(0) if match else None
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string to date object."""
        # Try common formats
        formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        # Default to today if parsing fails
        return date.today()
    
    def _extract_event_url(self, link, row) -> Optional[str]:
        """Extract event URL from link or row."""
        if link and link.get('href'):
            href = link.get('href')
            if href.startswith('http'):
                return href
            return f"{self.source_url}{href}" if href.startswith('/') else f"{self.source_url}/{href}"
        return None
    
    def _generate_event_id(self, event_date: date) -> str:
        """Generate unique event ID."""
        return f"{self.county_id}-{event_date.isoformat()}"
    
    def _determine_status(self, event_date: date) -> str:
        """Determine event status based on date."""
        today = date.today()
        if event_date < today:
            return 'ended'
        elif event_date == today:
            return 'live'
        else:
            return 'upcoming'
    
    def _extract_item_data(self, row, event_url: str) -> Optional[Dict[str, Any]]:
        """Extract item data from a table row or div."""
        try:
            cells = row.find_all(['td', 'div', 'span'])
            if not cells:
                return None
            
            # Try to find parcel ID (usually in first few columns)
            parcel_id_raw = None
            opening_bid = None
            item_url = None
            
            for i, cell in enumerate(cells[:5]):  # Check first 5 cells
                text = cell.get_text(strip=True)
                
                # Look for parcel ID pattern (numbers with dashes/slashes)
                if re.search(r'\d+[-./]\d+', text) and not parcel_id_raw:
                    parcel_id_raw = text
                
                # Look for dollar amounts (opening bid)
                if '$' in text and not opening_bid:
                    amount_match = re.search(r'\$[\d,]+\.?\d*', text)
                    if amount_match:
                        amount_str = amount_match.group(0).replace('$', '').replace(',', '')
                        try:
                            opening_bid = float(amount_str)
                        except ValueError:
                            pass
                
                # Look for links
                link = cell.find('a')
                if link and link.get('href') and not item_url:
                    href = link.get('href')
                    item_url = href if href.startswith('http') else f"{self.source_url}{href}"
            
            if parcel_id_raw:
                item_id = f"{self.county_id}-{self.normalize_parcel_id(parcel_id_raw)}"
                return {
                    'item_id': item_id,
                    'parcel_id_raw': parcel_id_raw,
                    'opening_bid': opening_bid,
                    'status': 'available',
                    'item_url': item_url or event_url,
                    'raw_json': {
                        'scraped_at': datetime.utcnow().isoformat(),
                        'html_snippet': str(row)[:500]
                    }
                }
        except Exception:
            pass
        
        return None
