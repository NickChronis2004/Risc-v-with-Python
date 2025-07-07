"""
Setup Script για RISC-V GUI Application
Εγκαθιστά όλα τα απαραίτητα dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        print("✅ Tkinter is available")
        return True
    except ImportError:
        print("❌ Tkinter not found. Please install python3-tkinter")
        return False

def check_risc_v_files():
    """Check if all RISC-V component files exist"""
    required_files = [
        "ALU.py",
        "RegisterFile.py", 
        "Memory.py",
        "InstructionDecoder.py",
        "ControlUnit.py",
        "Assembler.py",
        "MainCPU.py",
        "ExceptionHandling.py",
        "interface.py",
        "SimpleLogging.py",
        "LoggedMainCPU.py"
    ]
    
    missing_files = []
    existing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            existing_files.append(file)
    
    if existing_files:
        print(f"✅ Found {len(existing_files)} RISC-V component files:")
        for file in existing_files:
            print(f"  ✓ {file}")
    
    if missing_files:
        print(f"\n⚠️ Missing {len(missing_files)} RISC-V component files:")
        for file in missing_files:
            print(f"  ✗ {file}")
        print("\nMake sure all your RISC-V Python files are in the same directory!")
        return False
    
    print("✅ All RISC-V component files found")
    return True

def create_launcher():
    """Create launcher scripts for different platforms"""
    
    # Windows batch file
    if os.name == 'nt':
        with open("run_risc_v_gui.bat", "w") as f:
            f.write("@echo off\n")
            f.write("echo Starting RISC-V GUI...\n")
            f.write("python RiscV_GUI.py\n")
            f.write("pause\n")
        print("✅ Created run_risc_v_gui.bat")
    
    # Unix shell script
    else:
        with open("run_risc_v_gui.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("echo 'Starting RISC-V GUI...'\n")
            f.write("python3 RiscV_GUI.py\n")
        
        # Make executable
        os.chmod("run_risc_v_gui.sh", 0o755)
        print("✅ Created run_risc_v_gui.sh")

def main():
    """Main setup function"""
    print("🚀 RISC-V GUI Setup Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check tkinter
    if not check_tkinter():
        print("\nOn Ubuntu/Debian: sudo apt-get install python3-tkinter")
        print("On CentOS/RHEL: sudo yum install tkinter")
        print("On Windows: Tkinter comes with Python")
        return
    
    # Check RISC-V files
    if not check_risc_v_files():
        print("\n❌ Cannot continue without RISC-V component files")
        print("Please make sure all the Python files are in the current directory")
        return
    
    # Required packages
    packages = [
        "customtkinter",
        "pillow"
    ]
    
    print("\n📦 Installing required packages...")
    
    all_success = True
    for package in packages:
        print(f"\nInstalling {package}...")
        if not install_package(package):
            all_success = False
    
    if all_success:
        print("\n🎉 Setup completed successfully!")
        print("\nTo run the RISC-V GUI:")
        print("  python RiscV_GUI.py")
        
        # Create a launcher script
        print("\n📝 Creating launcher script...")
        create_launcher()
        
        print("\n🚀 You can now run the GUI using:")
        if os.name == 'nt':
            print("  run_risc_v_gui.bat")
        else:
            print("  ./run_risc_v_gui.sh")
        print("  or: python RiscV_GUI.py")
        
    else:
        print("\n❌ Some packages failed to install")
        print("Please install them manually:")
        for package in packages:
            print(f"  pip install {package}")

if __name__ == "__main__":
    main()