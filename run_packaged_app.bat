@echo off
echo Billiard Simulation Application
echo ==============================
echo.
echo 1. Run Billiard Simulation Visualization
echo 2. Run Billiard Analysis Dashboard
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo Starting Billiard Simulation...
    start dist\billiard_simulation\billiard_simulation.exe
) else if "%choice%"=="2" (
    echo Starting Billiard Dashboard...
    start dist\billiard_simulation\billiard_dashboard.exe
) else (
    echo Invalid choice. Please run the script again and select 1 or 2.
    pause
) 