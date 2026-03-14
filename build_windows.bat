@echo off
setlocal

echo Installing PySide6...
py -3.8 -m pip install "PySide6<6.6"

echo Building Typing Exam Practice EXE...
py -3.8 -m PyInstaller --onefile --windowed --name typing-exam-practice ^
    --hidden-import PySide6.QtCore ^
    --hidden-import PySide6.QtGui ^
    --hidden-import PySide6.QtWidgets ^
    --exclude-module tkinter ^
    --exclude-module _tkinter ^
    app.py

if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo Build complete.
echo EXE path: dist\typing-exam-practice.exe
