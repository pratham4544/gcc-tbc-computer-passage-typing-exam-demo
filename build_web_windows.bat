@echo off
setlocal

echo Installing dependencies...
pip install flask pyinstaller
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies.
    echo Make sure Python and pip are in your PATH.
    pause
    exit /b 1
)

echo.
echo Building Typing Exam Practice (Web) EXE...
pyinstaller --onefile --name typing-exam-web ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "Oct 2025 exam question paper;Oct 2025 exam question paper" ^
    --hidden-import flask ^
    --hidden-import jinja2.ext ^
    --exclude-module PySide6 ^
    --exclude-module tkinter ^
    --exclude-module _tkinter ^
    web_app.py

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Build complete!
echo EXE path: dist\typing-exam-web.exe
echo.
echo To run: double-click dist\typing-exam-web.exe
echo It will open your browser automatically at http://127.0.0.1:5000
echo.
pause
