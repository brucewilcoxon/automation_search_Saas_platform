"""
Unit tests for parcel ID normalization.
"""
import pytest
from scrapers.adapters.base import BaseCountyAdapter
from scrapers.adapters.miami_dade import MiamiDadeAdapter


class TestParcelNormalization:
    """Test parcel ID normalization logic."""
    
    def test_base_adapter_normalization(self):
        """Test base adapter normalization removes special characters."""
        adapter = BaseCountyAdapter("test", "http://test.com")
        
        # Test various formats
        assert adapter.normalize_parcel_id("30-2104-001-0010") == "30210400010010"
        assert adapter.normalize_parcel_id("123-45-678") == "12345678"
        assert adapter.normalize_parcel_id("5042-12-03-0120") == "504212030120"
        assert adapter.normalize_parcel_id("00-42-44-21-05-000-0010") == "004244210500000010"
        assert adapter.normalize_parcel_id("25-22-29-0000-00-042") == "252229000000042"
    
    def test_miami_dade_normalization(self):
        """Test Miami-Dade specific normalization."""
        adapter = MiamiDadeAdapter()
        
        # Miami-Dade format: 30-2104-001-0010 -> 30210400010010
        assert adapter.normalize_parcel_id("30-2104-001-0010") == "30210400010010"
        assert adapter.normalize_parcel_id("01-3120-005-0180") == "01312000050180"
        assert adapter.normalize_parcel_id("22-5044-012-0050") == "22504401200050"
    
    def test_empty_parcel_id(self):
        """Test normalization of empty strings."""
        adapter = BaseCountyAdapter("test", "http://test.com")
        assert adapter.normalize_parcel_id("") == ""
        assert adapter.normalize_parcel_id("   ") == ""
    
    def test_parcel_id_with_spaces(self):
        """Test normalization removes spaces."""
        adapter = BaseCountyAdapter("test", "http://test.com")
        assert adapter.normalize_parcel_id("30 - 2104 - 001 - 0010") == "30210400010010"
        assert adapter.normalize_parcel_id("123 45 678") == "12345678"
