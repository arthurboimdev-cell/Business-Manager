from gui.controller import TransactionController
from config.config import TABLE_NAME, TEST_TABLE
from db.init_db import init_db

if __name__ == "__main__":
    # Launch the GUI for the default table
    init_db(TEST_TABLE)
    app = TransactionController(TEST_TABLE)
    app.run()
