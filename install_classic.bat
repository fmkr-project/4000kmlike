@echo off

set name=4000kmlike

:: Run PyInstaller
call &pyinstaller -w --onefile ./src/main.py --name %name%

:: Modify file structure so that the executable is in the root directory$
move .\dist\%name%.exe .
rd /s /q .\dist

exit