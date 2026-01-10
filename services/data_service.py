import csv

class DataService:
    @staticmethod
    def export_to_csv(filename, transactions):
        """
        Export transactions list to a CSV file.
        """
        if not transactions:
            return
            
        keys = ["id", "transaction_date", "description", "quantity", "price", "total", "transaction_type", "supplier"]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write Header
            writer.writerow(keys)
            
            # Write Data
            for t in transactions:
                # Ensure we only write known keys in order
                row = [t.get(k, "") for k in keys]
                writer.writerow(row)



    @staticmethod
    def import_data(filename, existing_transactions):
        """
        Import data from CSV or Excel.
        """
        import os
        ext = os.path.splitext(filename)[1].lower()
        
        raw_rows = []
        if ext == '.xlsx':
            raw_rows = DataService._read_excel(filename)
        else:
            raw_rows = DataService._read_csv(filename)
            
        new_items = []
        
        
        # Build signature set of existing data
        existing_signatures = set()
        for t in existing_transactions:
            date_val = DataService._normalize_date(t.get('transaction_date', ''))
            try:
                price_val = "{:.2f}".format(float(t.get('price', 0.0)))
            except:
                price_val = "0.00"
            
            sig = (
                date_val,
                str(t.get('description', '')).strip().lower(),
                str(t.get('quantity', 0)), # Ensure int/str consistency
                price_val, 
                str(t.get('transaction_type', '')).strip().lower()
            )
            existing_signatures.add(sig)
            
        # Debug: Print a few existing signatures to understand state
        # print(f"DEBUG: Loaded {len(existing_signatures)} existing signatures.")
        # if existing_signatures:
        #    print(f"DEBUG Example: {list(existing_signatures)[0]}")

        for row in raw_rows:
            try:
                # Keys are guaranteed lowercase 
                r_date = DataService._normalize_date(row.get('transaction_date', '') or row.get('date', ''))
                r_desc = row.get('description', '') or row.get('desc', '') or row.get('item', '')
                r_qty = row.get('quantity', 0) or row.get('qty', 0)
                r_price_raw = row.get('price', 0.0) or row.get('amount', 0.0) or row.get('cost', 0.0)
                r_type = row.get('transaction_type', '') or row.get('type', '')
                r_supplier = row.get('supplier', '') or row.get('vendor', '')

                try:
                    r_price_fmt = "{:.2f}".format(float(r_price_raw))
                except:
                    r_price_fmt = "0.00"

                # Basic Validation
                if not r_date or not r_desc:
                    print(f"Skipping row missing date/desc: {row}")
                    continue

                sig = (
                    r_date, 
                    str(r_desc).strip().lower(),
                    str(int(float(r_qty))), # Handle "1.0" from Excel -> "1"
                    r_price_fmt,
                    str(r_type).strip().lower()
                )
                
                if sig not in existing_signatures:
                    # Check if maybe the description is VERY close? (Fuzzy match potential future step)
                    
                    new_items.append({
                        "date": r_date,
                        "description": r_desc,
                        "quantity": int(float(r_qty)),
                        "price": float(r_price_raw),
                        "type": r_type,
                        "supplier": r_supplier
                    })
                    existing_signatures.add(sig)
                else:
                    # print(f"Skipping duplicate: {r_desc}")
                    pass

            except ValueError as ve:
                 # print(f"Skipping row value error ({ve}): {row}")
                 continue
                 
        return new_items

    @staticmethod
    def _normalize_date(date_val):
        """
        Force date to YYYY-MM-DD string.
        Handles None, strings, datetime, date.
        """
        if not date_val:
            return ""
            
        try:
            if hasattr(date_val, 'strftime'):
                return date_val.strftime('%Y-%m-%d')
            
            # If string, try to parse or just take first 10 chars if it looks like ISO
            # 2025-01-01 00:00:00 -> 2025-01-01
            s_val = str(date_val).strip()
            if ' ' in s_val:
                s_val = s_val.split(' ')[0]
            return s_val
        except Exception:
            return str(date_val)

    @staticmethod
    def _read_excel(filename):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(filename, data_only=True)
            sheet = wb.active
            
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                return []
                
            headers = [str(h).strip().lower() for h in rows[0] if h]
            data = []
            
            for r in rows[1:]:
                # Zip headers with row values
                row_dict = {}
                for i, val in enumerate(r):
                    if i < len(headers):
                        # Convert datetime to string
                        if val and hasattr(val, 'strftime'):
                            row_dict[headers[i]] = val.strftime('%Y-%m-%d')
                        else:
                            row_dict[headers[i]] = val
                data.append(row_dict)
                
            return data
            
        except Exception as e:
            print(f"Excel import error: {e}")
            return []

    @staticmethod
    def _read_csv(filename):
        encodings = ['utf-8-sig', 'cp1252', 'iso-8859-1']
        
        for enc in encodings:
            try:
                with open(filename, 'r', encoding=enc) as f:
                    # Check header
                    sample = f.read(1024)
                    f.seek(0)
                    # has_header = csv.Sniffer().has_header(sample) # Sniffer triggers errors on some encodings
                    
                    try:
                        raw_reader = csv.reader(f)
                        headers = next(raw_reader)
                        f.seek(0)
                        
                        normalized_headers = [h.strip().lower() for h in headers]
                        reader = csv.DictReader(f, fieldnames=normalized_headers)
                        next(reader) # Skip header
                        
                        # Return full list to process commonly
                        return list(reader)
                        
                    except Exception as e:
                         print(f"CSV Parse error {enc}: {e}")
                         continue

            except UnicodeDecodeError:
                continue
            except Exception:
                pass
                
        print("All CSV encodings failed.")
        return []
