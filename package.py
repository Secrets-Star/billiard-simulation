"""
Packaging script for Billiard Simulation
"""
import os
import sys
import subprocess
import shutil

def check_dependencies():
    """Check and install required dependencies"""
    print("Checking dependencies...")
    
    # Required packages
    required_packages = [
        "numpy==1.24.3",
        "pygame==2.5.0", 
        "dash==2.9.3",
        "dash-bootstrap-components==1.4.1",
        "plotly==5.14.1",
        "pyinstaller"
    ]
    
    # Install packages
    for package in required_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")
            return False
    
    return True

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['billiard_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'numpy', 
        'pygame', 
        'dash', 
        'dash_bootstrap_components',
        'plotly',
        'flask',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Main visualization executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='billiard_simulation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Dashboard executable
exe2 = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='billiard_dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Collect both executables in a single distribution
coll = COLLECT(
    exe,
    exe2,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='billiard_simulation',
)
"""
    with open("billiard_simulation.spec", "w") as f:
        f.write(spec_content)
    
    print("Created spec file: billiard_simulation.spec")
    return True

def build_package():
    """Build the package using PyInstaller"""
    print("Building package with PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "--clean", "billiard_simulation.spec"])
        return True
    except subprocess.CalledProcessError:
        print("Failed to build package")
        return False

def create_launcher():
    """Create launcher scripts for the packaged application"""
    launcher_content = """@echo off
cd /d %~dp0
start dist\\billiard_simulation\\billiard_simulation.exe
"""
    
    dashboard_launcher_content = """@echo off
cd /d %~dp0
start dist\\billiard_simulation\\billiard_dashboard.exe --dashboard
"""
    
    with open("run_simulation.bat", "w") as f:
        f.write(launcher_content)
    
    with open("run_dashboard.bat", "w") as f:
        f.write(dashboard_launcher_content)
    
    print("Created launcher scripts: run_simulation.bat and run_dashboard.bat")
    return True

def create_distribution_zip():
    """Create a ZIP file for distribution"""
    print("Creating distribution ZIP file...")
    try:
        shutil.make_archive("billiard_simulation_package", "zip", "dist", "billiard_simulation")
        print("Created billiard_simulation_package.zip")
        return True
    except Exception as e:
        print(f"Failed to create ZIP file: {e}")
        return False

def main():
    """Main function"""
    print("===== Billiard Simulation Packaging Tool =====")
    
    # Check dependencies
    if not check_dependencies():
        print("Failed to install dependencies")
        return
    
    # Create spec file
    if not create_spec_file():
        print("Failed to create spec file")
        return
    
    # Build package
    if not build_package():
        print("Failed to build package")
        return
    
    # Create launcher scripts
    if not create_launcher():
        print("Failed to create launcher scripts")
        return
    
    # Create distribution ZIP
    create_distribution_zip()
    
    print("\n===== Packaging Complete =====")
    print("You can find the packaged application in the 'dist/billiard_simulation' folder.")
    print("Use run_simulation.bat to start the interactive visualization.")
    print("Use run_dashboard.bat to start the analysis dashboard.")
    
if __name__ == "__main__":
    main()
