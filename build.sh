#!/bin/bash

echo "Django App Generator Builder (PyQt6 Version)"
echo "============================================"
echo

# Install required packages if not already installed
echo "Installing/Updating required packages..."
python3 -m pip install --upgrade pyinstaller pyqt6
if [ $? -ne 0 ]; then
    echo "Failed to install required packages."
    exit 1
fi
echo "Required packages installed successfully."
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
    --name=DjangoAppGenerator-PyQt \
    --add-data="utils${separator}utils" \
    --add-data="gui${separator}gui" \
    --hidden-import=PyQt6 \
    --hidden-import=PyQt6.QtWidgets \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    main.py

if [ $? -ne 0 ]; then
    echo
    echo "Build failed. Trying alternative method..."
    echo
    
    python3 -c "import PyInstaller.__main__; PyInstaller.__main__.run(['--noconfirm', '--onefile', '--windowed', '--name=DjangoAppGenerator-PyQt', '--add-data=utils${separator}utils', '--add-data=gui${separator}gui', '--hidden-import=PyQt6', '--hidden-import=PyQt6.QtWidgets', '--hidden-import=PyQt6.QtCore', '--hidden-import=PyQt6.QtGui', 'main.py'])"
    
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
    chmod +x dist/DjangoAppGenerator-PyQt
fi