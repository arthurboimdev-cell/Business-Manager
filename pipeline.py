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

# replace_table_name removed - logic now handled by sys.frozen in config.py

def build_executable():
    print("Building executable...")
    # Kill existing process if running to avoid PermissionError
    subprocess.run(["taskkill", "/F", "/IM", "main.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    subprocess.run([
        PYTHON_EXE, "-m", "PyInstaller", 
        "--clean",
        "main.spec"
    ], check=True)
    print("Executable built in dist/ folder.")

def main():
    if run_tests():
        print("All tests passed")
        try:
            build_executable()
        except Exception as e:
            print(f"Build failed: {e}")
            sys.exit(1)
    else:
        print("Some tests failed. Aborting build.")

if __name__ == "__main__":
    main()
