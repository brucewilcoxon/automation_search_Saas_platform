"""
PDF report generator using Jinja2 templates and WeasyPrint.
"""
from typing import Optional, List
from io import BytesIO
from datetime import datetime
from jinja2 import Template
from weasyprint import HTML
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """PDF report generator."""
    
    def __init__(self):
        self.template = self._get_default_template()
    
    def generate_auction_report(
        self,
        parcel: Optional[object] = None,
        event: Optional[object] = None,
        comps_6m: Optional[List] = None,
        comps_12m: Optional[List] = None
    ) -> bytes:
        """
        Generate an auction PDF report.
        
        Args:
            parcel: Parcel object
            event: Auction event object
            comps_6m: Comparable sales from last 6 months
            comps_12m: Comparable sales from last 12 months
            
        Returns:
            PDF bytes
        """
        # Prepare template data
        data = self._prepare_template_data(parcel, event, comps_6m, comps_12m)
        
        # Render HTML
        template = Template(self.template)
        data['generated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content = template.render(**data)
        
        # Generate PDF
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()
        
        return pdf_bytes
    
    def _prepare_template_data(self, parcel, event, comps_6m, comps_12m):
        """Prepare data for template rendering."""
        data = {
            "parcel": None,
            "event": None,
            "comps_6m": [],
            "comps_12m": [],
            "has_enrichment": False
        }
        
        if parcel:
            data["parcel"] = {
                "id": parcel.id,
                "apn": parcel.apn or "N/A",
                "address": parcel.address or "Address not available",
                "county": parcel.county or "N/A",
                "state": parcel.state or "N/A",
                "acreage": f"{float(parcel.acreage):.2f}" if parcel.acreage else "N/A",
                "zoning": parcel.zoning or "Not available",
                "market_value": f"${float(parcel.market_value):,.2f}" if parcel.market_value else "N/A",
                "assessed_value": f"${float(parcel.assessed_value):,.2f}" if parcel.assessed_value else (f"${float(parcel.market_value):,.2f}" if parcel.market_value else "N/A"),
                "min_bid": f"${float(parcel.min_bid):,.2f}" if parcel.min_bid else "N/A",
                "taxes": f"${float(parcel.taxes):,.2f}" if parcel.taxes else "Not available",
                "flood_flag": "Yes" if parcel.flood_flag else ("No" if parcel.flood_flag is False else "Not available"),
                "latitude": f"{float(parcel.latitude):.4f}" if parcel.latitude else "N/A",
                "longitude": f"{float(parcel.longitude):.4f}" if parcel.longitude else "N/A",
                "last_updated": parcel.last_updated_at.strftime("%Y-%m-%d") if parcel.last_updated_at else "N/A"
            }
            data["has_enrichment"] = parcel.taxes is not None or parcel.assessed_value is not None or parcel.flood_flag is not None
        
        if event:
            data["event"] = {
                "id": event.id,
                "county": event.county,
                "state": event.state,
                "event_date": event.event_date.strftime("%Y-%m-%d") if event.event_date else "N/A",
                "status": event.status,
                "source_url": event.source_url or "N/A",
                "item_count": event.item_count or 0
            }
        
        if comps_6m:
            data["comps_6m"] = [
                {
                    "address": comp.address or "N/A",
                    "area": f"{float(comp.acreage):.1f} ac" if comp.acreage else "N/A",
                    "price": f"${float(comp.sold_price):,.0f}",
                    "date": comp.sold_date.strftime("%Y-%m-%d"),
                    "distance": f"{float(comp.distance):.1f} mi" if comp.distance else "N/A",
                    "similarity": int(round(float(comp.similarity_score)))
                }
                for comp in comps_6m[:10]
            ]
        
        if comps_12m:
            data["comps_12m"] = [
                {
                    "address": comp.address or "N/A",
                    "area": f"{float(comp.acreage):.1f} ac" if comp.acreage else "N/A",
                    "price": f"${float(comp.sold_price):,.0f}",
                    "date": comp.sold_date.strftime("%Y-%m-%d"),
                    "distance": f"{float(comp.distance):.1f} mi" if comp.distance else "N/A",
                    "similarity": int(round(float(comp.similarity_score)))
                }
                for comp in comps_12m[:10]
            ]
        
        return data
    
    def _get_default_template(self) -> str:
        """Get default HTML template for auction report."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Auction Report</title>
    <style>
        @page {
            size: letter;
            margin: 1in;
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333;
        }
        h1 {
            font-size: 18pt;
            color: #1a1a1a;
            border-bottom: 2px solid #333;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }
        h2 {
            font-size: 14pt;
            color: #2a2a2a;
            margin-top: 20px;
            margin-bottom: 10px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 3px;
        }
        .section {
            margin-bottom: 25px;
        }
        .row {
            display: flex;
            margin-bottom: 8px;
        }
        .label {
            font-weight: bold;
            width: 150px;
            flex-shrink: 0;
        }
        .value {
            flex: 1;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 9pt;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 6px;
            text-align: left;
        }
        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        .muted {
            color: #666;
            font-style: italic;
        }
        .footer {
            margin-top: 40px;
            padding-top: 10px;
            border-top: 1px solid #ccc;
            font-size: 8pt;
            color: #666;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Auction Parcel Report</h1>
    
    {% if parcel %}
    <div class="section">
        <h2>Parcel Information</h2>
        <div class="row"><span class="label">Parcel ID (APN):</span><span class="value">{{ parcel.apn }}</span></div>
        <div class="row"><span class="label">Address:</span><span class="value">{{ parcel.address }}</span></div>
        <div class="row"><span class="label">County / State:</span><span class="value">{{ parcel.county }}, {{ parcel.state }}</span></div>
        <div class="row"><span class="label">Acreage:</span><span class="value">{{ parcel.acreage }} acres</span></div>
        <div class="row"><span class="label">Zoning:</span><span class="value">{{ parcel.zoning }}</span></div>
        <div class="row"><span class="label">Market Value:</span><span class="value">{{ parcel.market_value }}</span></div>
        <div class="row"><span class="label">Assessed Value:</span><span class="value">{{ parcel.assessed_value }}</span></div>
        <div class="row"><span class="label">Minimum Bid:</span><span class="value">{{ parcel.min_bid }}</span></div>
        <div class="row"><span class="label">Annual Taxes:</span><span class="value">{{ parcel.taxes }}</span></div>
        <div class="row"><span class="label">Flood Zone:</span><span class="value">{{ parcel.flood_flag }}</span></div>
        <div class="row"><span class="label">Coordinates:</span><span class="value">{{ parcel.latitude }}, {{ parcel.longitude }}</span></div>
        <div class="row"><span class="label">Last Updated:</span><span class="value">{{ parcel.last_updated }}</span></div>
    </div>
    {% endif %}
    
    {% if event %}
    <div class="section">
        <h2>Auction Event Information</h2>
        <div class="row"><span class="label">Event ID:</span><span class="value">{{ event.id }}</span></div>
        <div class="row"><span class="label">Location:</span><span class="value">{{ event.county }}, {{ event.state }}</span></div>
        <div class="row"><span class="label">Event Date:</span><span class="value">{{ event.event_date }}</span></div>
        <div class="row"><span class="label">Status:</span><span class="value">{{ event.status }}</span></div>
        <div class="row"><span class="label">Total Items:</span><span class="value">{{ event.item_count }}</span></div>
        <div class="row"><span class="label">Source URL:</span><span class="value">{{ event.source_url }}</span></div>
    </div>
    {% endif %}
    
    {% if comps_6m %}
    <div class="section">
        <h2>Comparable Sales - Last 6 Months</h2>
        <table>
            <thead>
                <tr>
                    <th>Address</th>
                    <th>Area</th>
                    <th>Price</th>
                    <th>Date</th>
                    <th>Distance</th>
                    <th>Similarity</th>
                </tr>
            </thead>
            <tbody>
                {% for comp in comps_6m %}
                <tr>
                    <td>{{ comp.address }}</td>
                    <td>{{ comp.area }}</td>
                    <td>{{ comp.price }}</td>
                    <td>{{ comp.date }}</td>
                    <td>{{ comp.distance }}</td>
                    <td>{{ comp.similarity }}%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}
    
    {% if comps_12m %}
    <div class="section">
        <h2>Comparable Sales - Last 12 Months</h2>
        <table>
            <thead>
                <tr>
                    <th>Address</th>
                    <th>Area</th>
                    <th>Price</th>
                    <th>Date</th>
                    <th>Distance</th>
                    <th>Similarity</th>
                </tr>
            </thead>
            <tbody>
                {% for comp in comps_12m %}
                <tr>
                    <td>{{ comp.address }}</td>
                    <td>{{ comp.area }}</td>
                    <td>{{ comp.price }}</td>
                    <td>{{ comp.date }}</td>
                    <td>{{ comp.distance }}</td>
                    <td>{{ comp.similarity }}%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}
    
    {% if not comps_6m and not comps_12m %}
    <div class="section">
        <p class="muted">No comparable sales data available for this parcel.</p>
    </div>
    {% endif %}
    
    <div class="footer">
        <p>Generated on {{ generated_at }} | Auction Navigator Suite</p>
        <p class="muted">This report is for informational purposes only and does not constitute legal or financial advice.</p>
    </div>
</body>
</html>
        """
