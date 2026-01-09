import sys
import subprocess
import time
import os
import multiprocessing
import uvicorn
from gui.controller import TransactionController
from config.config import TABLE_NAME, SERVER_HOST, SERVER_PORT
from db.init_db import init_db

def start_server():
    """Start the FastAPI server as a subprocess"""
    # In a frozen app (PyInstaller), sys.executable is the exe itself.
    # We pass a flag to tell the new process to behave as a server.
    
    server_args = [sys.executable, __file__] if not getattr(sys, 'frozen', False) else [sys.executable]
    server_args.append("--server")
    
    process = subprocess.Popen(
        server_args,
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    print(f"Server started with PID: {process.pid}")
    return process

from server.main import app as server_app

def run_server_process():
    """Function to run the uvicorn server directly"""
    # Pass the app object directly instead of a string to avoid import errors in frozen exe
    uvicorn.run(server_app, host=SERVER_HOST, port=SERVER_PORT, log_level="info")

if __name__ == "__main__":
    multiprocessing.freeze_support() # Required for PyInstaller

    if "--server" in sys.argv:
        # 1. Run Server Only
        run_server_process()
    
    elif "--client" in sys.argv:
        # 2. Run Client Only (Expects server running elsewhere)
        print("Starting GUI (Client Only)...")
        init_db(TABLE_NAME) 
        try:
            app = TransactionController(TABLE_NAME)
            app.run()
        except Exception as e:
            print(f"Application error: {e}")

    else:
        # 3. Default: Run Both (Server + Client)
        init_db(TABLE_NAME)
        
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
            print("Shutting down server...")
            server_process.terminate()
            server_process.wait()
