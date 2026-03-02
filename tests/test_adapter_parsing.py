"""
Unit tests for adapter HTML parsing using saved fixtures.
"""
import pytest
from unittest.mock import Mock, patch
from scrapers.adapters.miami_dade import MiamiDadeAdapter
from pathlib import Path


class TestAdapterParsing:
    """Test adapter HTML parsing logic."""
    
    @pytest.fixture
    def adapter(self):
        """Create Miami-Dade adapter instance."""
        return MiamiDadeAdapter()
    
    @pytest.fixture
    def sample_html(self):
        """Load sample HTML fixture."""
        fixture_path = Path(__file__).parent / "fixtures" / "sample_auction_page.html"
        return fixture_path.read_text()
    
    def test_discover_auction_events(self, adapter, sample_html):
        """Test event discovery from HTML."""
        with patch.object(adapter, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.content = sample_html.encode('utf-8')
            mock_request.return_value = mock_response
            
            events = adapter.discover_auction_events()
            
            # Should find at least one event
            assert len(events) > 0
            
            # Check event structure
            event = events[0]
            assert 'event_id' in event
            assert 'event_date' in event
            assert 'event_url' in event
            assert 'status' in event
    
    def test_list_auction_items(self, adapter, sample_html):
        """Test item listing from HTML."""
        with patch.object(adapter, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.content = sample_html.encode('utf-8')
            mock_request.return_value = mock_response
            
            items = adapter.list_auction_items("http://test.com/auction")
            
            # Should find items
            assert len(items) > 0
            
            # Check item structure
            item = items[0]
            assert 'item_id' in item
            assert 'parcel_id_raw' in item
            assert 'opening_bid' in item or item.get('opening_bid') is None
            assert 'status' in item
    
    def test_parcel_id_extraction(self, adapter, sample_html):
        """Test parcel ID extraction from HTML."""
        with patch.object(adapter, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.content = sample_html.encode('utf-8')
            mock_request.return_value = mock_response
            
            items = adapter.list_auction_items("http://test.com/auction")
            
            # Should extract parcel IDs
            parcel_ids = [item.get('parcel_id_raw') for item in items if item.get('parcel_id_raw')]
            assert len(parcel_ids) > 0
            
            # Check format
            for pid in parcel_ids:
                assert '-' in pid or pid.isalnum()  # Should have dashes or be alphanumeric
