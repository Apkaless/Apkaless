@echo off
echo 🚀 Building Apkaless.py into executable...
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Check if PyInstaller is available
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ❌ Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

echo 🔧 Building executable...
pyinstaller --onefile --icon "apkaless.ico" --console --name "Apkaless" --distpath "dist" Apkaless.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Build completed successfully!
    echo 📦 Executable created in the 'dist' folder
    echo.
    echo 📂 Contents of dist folder:
    dir dist
) else (
    echo.
    echo ❌ Build failed!
    echo 🔍 Check the error messages above for details
)

echo.
pause
