from db.transactions import (
    write_transaction,
    read_transactions,
    delete_transaction,
    update_transaction
)

class TransactionModel:
    """
    Acts as an intermediary between the Controller and the Database functions.
    """
    def __init__(self, table_name):
        self.table_name = table_name

    def get_all_transactions(self):
        return read_transactions(table=self.table_name)

    def add_transaction(self, date, desc, qty, price, t_type, supplier=None):
        return write_transaction(date, desc, qty, price, t_type, supplier, table=self.table_name)

    def delete_transaction(self, t_id):
        delete_transaction(t_id, table=self.table_name)
    
    def update_transaction(self, t_id, date, desc, qty, price, t_type, supplier=None):
        update_transaction(t_id, date, desc, qty, price, t_type, supplier, table=self.table_name)
