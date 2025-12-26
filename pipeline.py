import subprocess
import sys
import os

MAIN_FILE = "main.py"

def run_tests():
    print("Running all tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", "-v"])
    return result.returncode == 0

def replace_table_name(new_table):
    """Replace the table used in start_gui() in main.py"""
    with open(MAIN_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(MAIN_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            if "start_gui(" in line:
                f.write(f"    start_gui({new_table})\n")
            else:
                f.write(line)
    print(f"Updated main.py to use {new_table}")

def build_executable():
    print("Building executable...")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", MAIN_FILE], check=True)
    print("Executable built in dist/ folder.")

def main():
    if run_tests():
        print("All tests passed ✅")

        # Temporarily switch to production table
        replace_table_name("TABLE_NAME")
        try:
            build_executable()
        finally:
            # Restore back to test table
            replace_table_name("TEST_TABLE")
    else:
        print("Some tests failed ❌. Aborting build.")

if __name__ == "__main__":
    main()
