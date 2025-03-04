@echo off
echo Django App Generator Builder
echo ============================
echo.

:: Install PyInstaller if not already installed
echo Installing/Updating PyInstaller...
python -m pip install --upgrade pyinstaller
if %ERRORLEVEL% neq 0 (
    echo Failed to install PyInstaller.
    exit /b 1
)
echo PyInstaller installed successfully.
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
    --name=DjangoAppGenerator ^
    --add-data="utils;utils" ^
    --add-data="gui;gui" ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Build failed. Trying alternative method...
    echo.
    
    python -c "import PyInstaller.__main__; PyInstaller.__main__.run(['--noconfirm', '--onefile', '--windowed', '--name=DjangoAppGenerator', '--add-data=utils;utils', '--add-data=gui;gui', '--hidden-import=tkinter', '--hidden-import=tkinter.ttk', 'main.py'])"
    
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