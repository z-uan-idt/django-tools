#!/bin/bash

echo "Django App Generator Builder"
echo "============================"
echo

# Install PyInstaller if not already installed
echo "Installing/Updating PyInstaller..."
python3 -m pip install --upgrade pyinstaller
if [ $? -ne 0 ]; then
    echo "Failed to install PyInstaller."
    exit 1
fi
echo "PyInstaller installed successfully."
echo

# Clean build directories
echo "Cleaning previous build files..."
rm -rf build dist
rm -f *.spec
echo "Clean completed."
echo

# Determine separator based on platform
separator=":"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Building for macOS..."
    separator=":"
else
    echo "Building for Linux..."
    separator=":"
fi

# Build the application
echo "Building application..."
echo

python3 -m PyInstaller \
    --noconfirm \
    --onefile \
    --windowed \
    --name=DjangoAppGenerator \
    --add-data="utils${separator}utils" \
    --add-data="gui${separator}gui" \
    --hidden-import=tkinter \
    --hidden-import=tkinter.ttk \
    main.py

if [ $? -ne 0 ]; then
    echo
    echo "Build failed. Trying alternative method..."
    echo
    
    python3 -c "import PyInstaller.__main__; PyInstaller.__main__.run(['--noconfirm', '--onefile', '--windowed', '--name=DjangoAppGenerator', '--add-data=utils${separator}utils', '--add-data=gui${separator}gui', '--hidden-import=tkinter', '--hidden-import=tkinter.ttk', 'main.py'])"
    
    if [ $? -ne 0 ]; then
        echo
        echo "All build methods failed."
        exit 1
    fi
fi

echo
echo "Build completed successfully."
echo "Executable is located in the dist folder."
echo

# Make the executable executable on macOS/Linux
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux"* ]]; then
    chmod +x dist/DjangoAppGenerator
fi