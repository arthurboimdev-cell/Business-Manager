from client.api_client import APIClient

class TransactionModel:
    """
    Acts as an intermediary between the Controller and the API.
    """
    def __init__(self, table_name):
        self.table_name = table_name
        # Note: table_name is less relevant on client side now as API handles it, 
        # but kept for compatibility or potentially sending as param if API supported dynamic tables.

    def get_all_transactions(self):
        return APIClient.get_all_transactions()

    def add_transaction(self, date, desc, qty, price, t_type, supplier=None):
        return APIClient.add_transaction(date, desc, qty, price, t_type, supplier)

    def delete_transaction(self, t_id):
        APIClient.delete_transaction(t_id)
    
    def update_transaction(self, t_id, date, desc, qty, price, t_type, supplier=None):
        APIClient.update_transaction(t_id, date, desc, qty, price, t_type, supplier)
