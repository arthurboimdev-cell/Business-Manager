import sys
import subprocess
import time
import os
import multiprocessing
import uvicorn
from gui.controller import TransactionController
from config.config import TABLE_NAME, SERVER_HOST, SERVER_PORT, TRANSACTIONS_SCHEMA, PRODUCTS_TABLE_NAME, PRODUCTS_SCHEMA, MATERIALS_TABLE, MATERIALS_SCHEMA
from db.init_db import init_db

def start_server():
    """Start the FastAPI server as a subprocess"""
    # In a frozen app (PyInstaller), sys.executable is the exe itself.
    # We pass a flag to tell the new process to behave as a server.
    
    server_args = [sys.executable, __file__] if not getattr(sys, 'frozen', False) else [sys.executable]
    server_args.append("--server")
    
    process = subprocess.Popen(
        server_args
    )
    print(f"Server started with PID: {process.pid}")
    return process

from server.main import app as server_app

def run_server_process():
    """Function to run the uvicorn server directly"""
    # Fix for PyInstaller noconsole mode where stdout/stderr are None
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')

    # Pass the app object directly instead of a string to avoid import errors in frozen exe
    uvicorn.run(server_app, host=SERVER_HOST, port=SERVER_PORT, log_level="info", use_colors=False)

import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

if __name__ == "__main__":
    multiprocessing.freeze_support() # Required for PyInstaller

    if "--server" in sys.argv:
        # 1. Run Server Only
        run_server_process()
    
    elif "--client" in sys.argv:
        # 2. Run Client Only (Expects server running elsewhere)
        print("Starting GUI (Client Only)...")
        init_db(TABLE_NAME, TRANSACTIONS_SCHEMA)
        init_db(PRODUCTS_TABLE_NAME, PRODUCTS_SCHEMA) 
        init_db(MATERIALS_TABLE, MATERIALS_SCHEMA) 
        try:
            app = TransactionController(TABLE_NAME)
            app.run()
        except Exception as e:
            print(f"Application error: {e}")

    else:
        # 3. Default: Run Both (Server + Client)
        init_db(TABLE_NAME, TRANSACTIONS_SCHEMA)
        init_db(PRODUCTS_TABLE_NAME, PRODUCTS_SCHEMA)
        init_db(MATERIALS_TABLE, MATERIALS_SCHEMA)
        
        # DEBUG: Print environment info
        is_frozen_state = getattr(sys, 'frozen', False)
        print(f"DEBUG: sys.frozen={is_frozen_state}")
        print(f"DEBUG: Using Tables -> Transactions: '{TABLE_NAME}', Products: '{PRODUCTS_TABLE_NAME}', Materials: '{MATERIALS_TABLE}'")

        server_process = None
        if is_port_in_use(SERVER_PORT):
            print(f"Port {SERVER_PORT} is already in use. Assuming Server is running.")
        else:
            print("Starting AurumCandles Server...")
            server_process = start_server()
            # Wait for server to be ready
            time.sleep(3)
        
        try:
            print("Starting GUI...")
            app = TransactionController(TABLE_NAME)
            app.run()
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            if server_process:
                print("Shutting down server...")
                server_process.terminate()
                server_process.wait()
