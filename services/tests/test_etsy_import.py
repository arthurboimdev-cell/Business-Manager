"""
Tests for Etsy CSV Import Service
"""

import pytest
import os
import csv
from unittest.mock import patch, MagicMock
from services.etsy_import import (
    parse_etsy_csv,
    download_image_from_url,
    check_product_exists,
    import_etsy_products
)


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample Etsy CSV file for testing."""
    csv_path = tmp_path / "test_etsy.csv"
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write CSV header
        writer.writerow([
            'TITLE', 'DESCRIPTION', 'PRICE', 'CURRENCY_CODE', 'QUANTITY',
            'TAGS', 'MATERIALS', 'IMAGE1', 'IMAGE2', 'IMAGE3', 'IMAGE4',
            'IMAGE5', 'IMAGE6', 'IMAGE7', 'IMAGE8', 'IMAGE9', 'IMAGE10',
            'VARIATION 1 TYPE', 'VARIATION 1 NAME', 'VARIATION 1 VALUES',
            'VARIATION 2 TYPE', 'VARIATION 2 NAME', 'VARIATION 2 VALUES', 'SKU'
        ])
        
        # Write sample product
        writer.writerow([
            'Test Rose Candle',  # TITLE
            'Beautiful handmade rose candle',  # DESCRIPTION
            '35',  # PRICE
            'CAD',  # CURRENCY_CODE
            '5',  # QUANTITY
            'Rose_Candle,Soy_Wax',  # TAGS
            'Soy',  # MATERIALS
            'https://example.com/image1.jpg',  # IMAGE1
            'https://example.com/image2.jpg',  # IMAGE2
            '',  # IMAGE3-10 empty
            '', '', '', '', '', '', '',
            'Colour',  # VARIATION 1 TYPE
            'Primary colour',  # VARIATION 1 NAME
            'Pink,White',  # VARIATION 1 VALUES
            '',  # VARIATION 2 TYPE
            '',  # VARIATION 2 NAME
            '',  # VARIATION 2 VALUES
            'TEST-SKU-001'  # SKU
        ])
    
    return str(csv_path)


def test_parse_etsy_csv(sample_csv_file):
    """Test CSV parsing returns correct product data."""
    products = parse_etsy_csv(sample_csv_file)
    
    assert len(products) == 1
    
    product = products[0]
    assert product['title'] == 'Test Rose Candle'
    assert product['description'] == 'Beautiful handmade rose candle'
    assert product['selling_price'] == 35.0
    assert product['stock_quantity'] == 5
    assert product['sku'] == 'TEST-SKU-001'
    assert product['wax_type'] == 'Soy'
    
    # Check etsy_data
    assert 'etsy_data' in product
    assert product['etsy_data']['currency'] == 'CAD'
    assert product['etsy_data']['tags'] == 'Rose_Candle,Soy_Wax'
    
    # Check variation data
    assert 'variation_1' in product['etsy_data']
    assert product['etsy_data']['variation_1']['type'] == 'Colour'
    
    # Check images
    assert '_image_urls' in product
    assert len(product['_image_urls']) == 2
    assert product['_image_urls'][0] == 'https://example.com/image1.jpg'


@patch('services.etsy_import.requests.get')
def test_download_image_from_url_success(mock_get):
    """Test successful image download."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'fake_image_data'
    mock_get.return_value = mock_response
    
    result = download_image_from_url('https://example.com/image.jpg', 'Test Product')
    
    assert result == b'fake_image_data'
    mock_get.assert_called_once_with('https://example.com/image.jpg', timeout=10)


@patch('services.etsy_import.requests.get')
def test_download_image_from_url_failure(mock_get):
    """Test failed image download returns None."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    result = download_image_from_url('https://example.com/missing.jpg', 'Test Product')
    
    assert result is None


@patch('services.etsy_import.requests.get')
def test_download_image_from_url_timeout(mock_get):
    """Test timeout handling."""
    import requests
    mock_get.side_effect = requests.Timeout()
    
    result = download_image_from_url('https://example.com/slow.jpg', 'Test Product')
    
    assert result is None


@patch('services.etsy_import.get_products')
def test_check_product_exists_by_sku(mock_get_products):
    """Test duplicate detection by SKU."""
    mock_get_products.return_value = [
        {'id': 1, 'title': 'Existing Product', 'sku': 'TEST-123'},
        {'id': 2, 'title': 'Another Product', 'sku': 'TEST-456'}
    ]
    
    # Should find by SKU
    assert check_product_exists('Different Title', 'TEST-123') is True
    
    # Should not find non-existent SKU
    assert check_product_exists('New Product', 'TEST-999') is False


@patch('services.etsy_import.get_products')
def test_check_product_exists_by_title(mock_get_products):
    """Test duplicate detection by title (case-insensitive)."""
    mock_get_products.return_value = [
        {'id': 1, 'title': 'Rose Candle', 'sku': None}
    ]
    
    # Should find by title (case-insensitive)
    assert check_product_exists('rose candle', None) is True
    assert check_product_exists('Rose Candle', None) is True
    assert check_product_exists('  Rose Candle  ', None) is True
    
    # Should not find different title
    assert check_product_exists('Different Candle', None) is False


@patch('services.etsy_import.create_product')
@patch('services.etsy_import.add_product_image')
@patch('services.etsy_import.download_image_from_url')
@patch('services.etsy_import.check_product_exists')
def test_import_etsy_products_success(
    mock_check_exists,
    mock_download,
    mock_add_image,
    mock_create,
    sample_csv_file
):
    """Test successful product import."""
    mock_check_exists.return_value = False  # No duplicates
    mock_create.return_value = 123  # Product ID
    mock_download.return_value = b'fake_image'
    
    stats = import_etsy_products(sample_csv_file)
    
    assert stats['imported'] == 1
    assert stats['skipped_duplicates'] == 0
    assert stats['skipped_errors'] == 0
    
    # Verify create_product was called
    mock_create.assert_called_once()
    
    # Verify images were downloaded
    assert mock_download.call_count == 2  # 2 images in sample


@patch('services.etsy_import.check_product_exists')
def test_import_etsy_products_skip_duplicates(mock_check_exists, sample_csv_file):
    """Test that duplicates are skipped."""
    mock_check_exists.return_value = True  # All are duplicates
    
    stats = import_etsy_products(sample_csv_file)
    
    assert stats['imported'] == 0
    assert stats['skipped_duplicates'] == 1
    assert stats['skipped_errors'] == 0


@patch('services.etsy_import.create_product')
@patch('services.etsy_import.check_product_exists')
def test_import_etsy_products_error_handling(mock_check_exists, mock_create, sample_csv_file):
    """Test error handling during import."""
    mock_check_exists.return_value = False
    mock_create.side_effect = Exception("Database error")
    
    stats = import_etsy_products(sample_csv_file)
    
    assert stats['imported'] == 0
    assert stats['skipped_duplicates'] == 0
    assert stats['skipped_errors'] == 1
