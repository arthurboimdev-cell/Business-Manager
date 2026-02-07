"""
Etsy CSV Import Service

Handles parsing Etsy CSV exports and importing products into the database.
Includes image downloading from URLs and duplicate detection.
"""

import csv
import json
import requests
from io import BytesIO
from typing import List, Dict, Optional, Callable
from db.products import create_product, get_products, add_product_image


def parse_etsy_csv(csv_path: str) -> List[Dict]:
    """
    Parse Etsy CSV file and return list of product dictionaries.
    
    Args:
        csv_path: Path to the Etsy CSV file
        
    Returns:
        List of product dictionaries with mapped fields
    """
    products = []
    
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Skip rows without title
            if not row.get('TITLE'):
                continue
                
            # Map Etsy fields to AurumCandles product schema
            product = {
                'title': row['TITLE'].strip(),
                'description': row.get('DESCRIPTION', '').strip(),
                'selling_price': float(row['PRICE']) if row.get('PRICE') else 0.0,
                'stock_quantity': int(row['QUANTITY']) if row.get('QUANTITY') else 0,
                'sku': row.get('SKU', '').strip() or None,
                'wax_type': row.get('MATERIALS', '').strip() or 'Soy',  # Default to Soy
            }
            
            # Store Etsy-specific data as JSON
            etsy_data = {
                'tags': row.get('TAGS', ''),
                'currency': row.get('CURRENCY_CODE', 'CAD'),
                'materials': row.get('MATERIALS', ''),
            }
            
            # Parse variations if present
            if row.get('VARIATION 1 TYPE'):
                etsy_data['variation_1'] = {
                    'type': row.get('VARIATION 1 TYPE', ''),
                    'name': row.get('VARIATION 1 NAME', ''),
                    'values': row.get('VARIATION 1 VALUES', ''),
                }
            
            if row.get('VARIATION 2 TYPE'):
                etsy_data['variation_2'] = {
                    'type': row.get('VARIATION 2 TYPE', ''),
                    'name': row.get('VARIATION 2 NAME', ''),
                    'values': row.get('VARIATION 2 VALUES', ''),
                }
            
            product['etsy_data'] = etsy_data
            
            # Collect image URLs (IMAGE1 through IMAGE10)
            images = []
            for i in range(1, 11):
                image_url = row.get(f'IMAGE{i}', '').strip()
                if image_url:
                    images.append(image_url)
            
            product['_image_urls'] = images  # Temporary field for processing
            
            products.append(product)
    
    return products


def download_image_from_url(url: str, product_title: str) -> Optional[bytes]:
    """
    Download image from URL and return binary data.
    
    Args:
        url: Image URL to download
        product_title: Product title for logging
        
    Returns:
        Binary image data or None if download fails
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to download image for '{product_title}': HTTP {response.status_code}")
            return None
    except requests.Timeout:
        print(f"Timeout downloading image for '{product_title}': {url}")
        return None
    except Exception as e:
        print(f"Error downloading image for '{product_title}': {e}")
        return None


def check_product_exists(title: str, sku: Optional[str] = None) -> bool:
    """
    Check if product already exists in database by SKU or title.
    
    Args:
        title: Product title to check
        sku: Optional SKU to check
        
    Returns:
        True if product exists, False otherwise
    """
    products = get_products()
    
    for product in products:
        # Check by SKU first (if provided)
        if sku and product.get('sku') == sku:
            return True
        
        # Check by exact title match (case-insensitive)
        if product['title'].strip().lower() == title.strip().lower():
            return True
    
    return False


def import_etsy_products(
    csv_path: str,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, int]:
    """
    Import products from Etsy CSV file.
    
    Args:
        csv_path: Path to Etsy CSV file
        progress_callback: Optional callback(current, total, status_message)
        
    Returns:
        Dictionary with import statistics:
        {
            'imported': number of products imported,
            'skipped_duplicates': number of duplicates skipped,
            'skipped_errors': number of products skipped due to errors
        }
    """
    stats = {
        'imported': 0,
        'skipped_duplicates': 0,
        'skipped_errors': 0
    }
    
    # Parse CSV
    try:
        products = parse_etsy_csv(csv_path)
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return stats
    
    total = len(products)
    
    for idx, product_data in enumerate(products, 1):
        title = product_data['title']
        sku = product_data.get('sku')
        
        # Update progress
        if progress_callback:
            progress_callback(idx, total, f"Processing: {title[:50]}...")
        
        # Check for duplicates
        if check_product_exists(title, sku):
            print(f"Skipping duplicate: {title}")
            stats['skipped_duplicates'] += 1
            continue
        
        try:
            # Extract image URLs before creating product
            image_urls = product_data.pop('_image_urls', [])
            
            # Download first image for main product image field
            if image_urls:
                first_image = download_image_from_url(image_urls[0], title)
                if first_image:
                    product_data['image'] = first_image
            
            # Create product in database (now with main image)
            product_id = create_product(product_data)
            
            # Download and add remaining images to product_images table
            # Start from index 1 (skip first image as it's already the main image)
            for idx, image_url in enumerate(image_urls[1:], start=1):
                image_data = download_image_from_url(image_url, title)
                if image_data:
                    add_product_image(product_id, image_data, display_order=idx)
                else:
                    print(f"Skipped image {idx + 1} for '{title}'")
            
            stats['imported'] += 1
            print(f"Imported: {title}")
            
        except Exception as e:
            print(f"Error importing '{title}': {e}")
            stats['skipped_errors'] += 1
            continue
    
    return stats
