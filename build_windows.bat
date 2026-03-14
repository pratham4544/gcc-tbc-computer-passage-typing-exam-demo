@echo off
setlocal

echo Building Typing Exam Practice EXE...
py -3.8 -m PyInstaller --onefile --windowed --name typing-exam-practice app.py

if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo Build complete.
echo EXE path: dist\typing-exam-practice.exe
