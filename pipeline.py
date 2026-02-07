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

    # Copy config folder to dist
    print("Copying config files...")
    import shutil
    dist_config = os.path.join("dist", "config")
    if os.path.exists(dist_config):
        shutil.rmtree(dist_config)
    
    # We want config.json and local.env. 
    # Just copying the whole folder is easiest, but maybe filter?
    # shutil.copytree("config", dist_config)
    
    os.makedirs(dist_config, exist_ok=True)
    
    # Copy specific files
    for f in ["config.json", "local.env", "features.json"]:
        src = os.path.join("config", f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dist_config, f))
            print(f"Copied {f}")


def copy_to_desktop():
    """Copy the built executable to the user's desktop"""
    import shutil
    
    # Get desktop path
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Source exe
    exe_source = os.path.join("dist", "main.exe")
    
    if not os.path.exists(exe_source):
        print(f"Warning: Executable not found at {exe_source}")
        return
    
    # Destination on desktop
    exe_dest = os.path.join(desktop, "main.exe")
    
    try:
        shutil.copy2(exe_source, exe_dest)
        print(f"[Done] Executable copied to Desktop: {exe_dest}")
    except Exception as e:
        print(f"Warning: Could not copy to desktop: {e}")


def main():
    if run_tests():
        print("All tests passed")
        try:
            build_executable()
            copy_to_desktop()
        except Exception as e:
            print(f"Build failed: {e}")
            sys.exit(1)
    else:
        print("Some tests failed. Aborting build.")

if __name__ == "__main__":
    main()
