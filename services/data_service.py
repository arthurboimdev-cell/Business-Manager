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
