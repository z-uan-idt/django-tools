@echo off
echo Django App Generator Builder (PyQt6 Version)
echo ============================================
echo.

:: Install required packages if not already installed
echo Installing/Updating required packages...
python -m pip install --upgrade pyinstaller pyqt6
if %ERRORLEVEL% neq 0 (
    echo Failed to install required packages.
    exit /b 1
)
echo Required packages installed successfully.
echo.

:: Clean build directories
echo Cleaning previous build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec 2>nul
echo Clean completed.
echo.

:: Build the application
echo Building application...
echo.

python -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name=DjangoAppGenerator-PyQt ^
    --add-data="utils;utils" ^
    --add-data="gui;gui" ^
    --hidden-import=PyQt6 ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Build failed. Trying alternative method...
    echo.
    
    python -c "import PyInstaller.__main__; PyInstaller.__main__.run(['--noconfirm', '--onefile', '--windowed', '--name=DjangoAppGenerator-PyQt', '--add-data=utils;utils', '--add-data=gui;gui', '--hidden-import=PyQt6', '--hidden-import=PyQt6.QtWidgets', '--hidden-import=PyQt6.QtCore', '--hidden-import=PyQt6.QtGui', 'main.py'])"
    
    if %ERRORLEVEL% neq 0 (
        echo.
        echo All build methods failed.
        exit /b 1
    )
)

echo.
echo Build completed successfully.
echo Executable is located in the dist folder.
echo.

pause