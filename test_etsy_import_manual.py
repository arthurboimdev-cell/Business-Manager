"""
Manual test script to verify Etsy CSV import with actual data.
Run this to test the import functionality before using the GUI.
"""

import pytest
from services.etsy_import import import_etsy_products

@pytest.mark.skip(reason="Manual test - requires actual Etsy CSV file")
def test_import():
    csv_path = r"C:\Users\arthu\Downloads\EtsyListingsDownload.csv"
    
    print("=" * 60)
    print("Testing Etsy CSV Import")
    print("=" * 60)
    
    def progress(current, total, message):
        print(f"[{current}/{total}] {message}")
    
    print(f"\nImporting from: {csv_path}\n")
    
    try:
        stats = import_etsy_products(csv_path, progress)
        
        print("\n" + "=" * 60)
        print("IMPORT COMPLETE")
        print("=" * 60)
        print(f"Imported: {stats['imported']} products")
        print(f"Skipped (duplicates): {stats['skipped_duplicates']}")
        print(f"Skipped (errors): {stats['skipped_errors']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_import()
