#!/bin/sh

name='4000kmlike'

# Run PyInstaller
pyinstaller -w --onefile ./src/main.py --name $name

# Modify file structure so that the executable is in the root directory
mv ./dist/$name.exe .
rm -r ./dist