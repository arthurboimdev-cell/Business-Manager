import subprocess
import sys
import os

MAIN_FILE = "main.py"

def get_python_executable():
    """Get the python executable to use. Prioritizes .venv if found."""
    # Check for .venv in current directory
    venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable

PYTHON_EXE = get_python_executable()

def run_tests():
    print("Running all tests...")
    result = subprocess.run([PYTHON_EXE, "-m", "pytest", "-v"])
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
    subprocess.run([
        PYTHON_EXE, "-m", "PyInstaller", 
        "--onefile", 
        "--noconsole",
        "--add-data", "config/local.env;config", 
        MAIN_FILE
    ], check=True)
    print("Executable built in dist/ folder.")

def main():
    if run_tests():
        print("All tests passed")

        # Temporarily switch to production table
        replace_table_name("TABLE_NAME")
        try:
            build_executable()
        finally:
            # Restore back to test table
            replace_table_name("TEST_TABLE")
    else:
        print("Some tests failed. Aborting build.")

if __name__ == "__main__":
    main()
