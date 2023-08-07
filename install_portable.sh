#!/bin/sh

name='4000kmlike'
pyinstaller_path=../'portable python-3.10.5 x64/app/python/scripts/pyinstaller.exe'
# TODO specify a global pyinstaller path

# Run PyInstaller
"$pyinstaller_path" -w --onefile ./src/main.py --name $name

# Modify file structure so that the executable is in the root directory
mv ./dist/$name.exe .
rm -r ./dist