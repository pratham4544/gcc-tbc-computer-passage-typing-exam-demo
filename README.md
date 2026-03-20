# Typing Exam Practice App

Offline desktop typing-practice app for Windows 7/10 candidates.

## Features

- English 30 WPM timed test for 7 minutes
- English 40 WPM timed test for 7 minutes
- Marathi 30 test for 7 minutes
- Practice mode without timer for English or Marathi
- Random built-in passages
- Word-matching accuracy calculation
- On-screen result summary with elapsed time, matched words, accuracy, and WPM
- Marathi input area uses the `Mangal` font and assumes `ISM V6` is already running in the background

## How to Run the Software

### Option 1: Run Directly with Python (Linux/Mac/Windows)

**Prerequisites:**
- Python 3.8 or higher
- PySide6: `pip install "PySide6<6.6"`

**Run the application:**
```bash
python app.py
```

### Option 2: Run the Pre-built EXE (Windows Only)

Just double-click `dist/typing-exam-practice.exe` (after building it)

## How to Build .EXE File (Windows)

### Easy Method - Use the Batch Script

On Windows, simply double-click or run:
```bash
build_windows.bat
```

This automatically:
- Installs PySide6
- Builds the .exe using PyInstaller
- Creates `dist/typing-exam-practice.exe`

### Manual Method - Build Step-by-Step

1. **Install Python 3.8+ and pyinstaller:**
   ```bash
   pip install "PySide6<6.6"
   pip install pyinstaller==5.13.2
   ```

2. **Build the EXE:**
   ```bash
   pyinstaller --onefile --windowed --name typing-exam-practice ^
       --hidden-import PySide6.QtCore ^
       --hidden-import PySide6.QtGui ^
       --hidden-import PySide6.QtWidgets ^
       --exclude-module tkinter ^
       --exclude-module _tkinter ^
       app.py
   ```

3. **The .exe file will be at:**
   ```
   dist/typing-exam-practice.exe
   ```

## How to Type Marathi (ISM - Indian Standard Method)

### Windows Users:
1. **Install ISM Software** on your Windows machine
2. **Press Scroll Lock key** to activate Marathi typing mode
3. **Start typing** - English keys will now produce Marathi characters
4. **Press Scroll Lock again** to switch back to English

### Linux Users:
1. **Install ISM packages:**
   ```bash
   sudo apt install ibus-indic-smc ibus-engine-indic
   ```
2. **Add Marathi input method** in your system settings
3. **Switch input method** using keyboard shortcut (usually Ctrl+Space or Super+Space)
4. **Start typing** in Marathi mode

### macOS Users:
1. **Go to System Preferences → Keyboard → Input Sources**
2. **Add "Marathi - Inscript"** layout
3. **Switch using Ctrl+Space** or the input menu
4. **Start typing** in Marathi mode

**Important:** Make sure ISM is active before starting the typing test. The application will display Marathi text, but you need ISM running to type Marathi characters.

## Installation (Windows Users)

1. Download `typing-exam-practice.exe` from `dist/` folder
2. Place it anywhere on your computer
3. Double-click to run (no installation needed)
4. No dependencies to install - everything is included

## Local Run

Recommended Python version for Windows 7 compatibility: `Python 3.8.x 64-bit`

```bash
python app.py
```

## Build Windows EXE

Install PyInstaller:

```bash
pip install pyinstaller==5.13.2
```

Create a single-file executable:

```bash
pyinstaller --onefile --windowed --name typing-exam-practice app.py
```

Or on Windows:

```bat
build_windows.bat
```

The generated installer-free executable will be available at:

```text
dist/typing-exam-practice.exe
```

## Build From GitHub

This repository includes a GitHub Actions workflow at `.github/workflows/build-windows.yml`.

- Push a tag like `v1.0.0` to build the Windows `.exe`
- GitHub Actions will build `typing-exam-practice.exe` on Windows
- The file will be available in:
  - the workflow artifact
  - the GitHub Release for that tag

## Load DOCX Question Papers

If you copy your exam-paper folder into:

```text
/home/pratham/Desktop/projects/gcctbc/Oct 2025 exam question paper
```

the app will automatically scan `.docx` files for:

- English 30 WPM
- English 40 WPM
- Marathi 30 WPM
- Marathi 40 WPM
- Hindi 30 WPM
- Hindi 40 WPM

When matching folders are found, the app will use those passages instead of the built-in sample passages.

## Notes

- To support Windows 7, build the executable on a Windows 7/10 machine using Python 3.8 64-bit.
- `ISM V6` is not bundled in this app. It must be installed and running separately for Marathi typing.
- Accuracy is calculated by comparing typed words with passage words in the same sequence.
- On Windows, the app prefers `Mangal`, then `Nirmala UI`, including the bundled `Nirmala UI Regular.ttf` when it can be registered privately.
- On Ubuntu, Marathi may render as rectangular boxes if Devanagari fonts are not installed. Install a package such as `fonts-noto-core`, and the app will fall back to `Noto Sans Devanagari` when available.
