from gui.controller import TransactionController
from config.config import TABLE_NAME, TEST_TABLE

if __name__ == "__main__":
    # Launch the GUI for the default table
    app = TransactionController(TEST_TABLE)
    app.run()
