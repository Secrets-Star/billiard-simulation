@echo off
echo Building Billiard Simulation Package...

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Build using the spec file
pyinstaller --clean billiard_simulation.spec

echo.
echo Build complete! 
echo.
echo You can find the packaged application in the 'dist\billiard_simulation' folder.
echo.
echo Usage:
echo   - billiard_simulation.exe - Run the interactive visualization
echo   - billiard_dashboard.exe --dashboard - Run the analysis dashboard
echo.
pause
