# Marathi Font Fix - Guide

## Issue
Marathi text in the PySide6 application was not rendering properly, while it worked correctly on websites like majhinaukri.in which use ISM (Indian Standard Method) for typing.

## Root Cause
The application was not prioritizing the best Indic font (Noto Sans Devanagari) for rendering Marathi text, and font rendering wasn't optimized for proper antialiasing.

## Fixes Applied

### 1. **Font Priority Updated** ✅
   - **Before**: Prioritized Mangal/Nirmala UI first
   - **After**: Now prioritizes Noto Sans Devanagari (industry standard for Indic scripts)
   - **File**: `app.py` - `_resolve_indic_font()` method

### 2. **Font Rendering Enhanced** ✅
   - Added antialiasing strategy for Devanagari text rendering
   - **File**: `app.py` - `_get_display_font()` method

### 3. **Font Info Display** ✅
   - Added font information label that updates when language changes
   - Shows which font is currently in use for Marathi/Hindi
   - **File**: `app.py` - `_sync_custom_font()` method

## System Status
✅ **Noto Sans Devanagari is installed** on your system
✅ **Best font available for Marathi rendering**
✅ **All fixes have been applied**

## Usage with ISM (Indian Standard Method)

### Linux
The application now supports typing Marathi using ISM with the system's default input method:

1. Install ISM if not already installed:
   ```bash
   sudo apt install ibus-indic-smc ibus-engine-indic
   ```

2. Add Marathi input method to your system:
   - Go to Settings → Language Support
   - In Input Method, select "IBus"
   - Add "Marathi (Inscript)" or "Marathi" input method

3. Switch input method (usually Ctrl+Space or Super+Space) and start typing

### Windows
For Windows users, you can use:
- **Microsoft IME (Input Method Editor)** - Built into Windows
- Go to Settings → Language → Add language → Marathi
- Select "Marathi (Inscript)" layout

After adding the input method, you can select it from the taskbar and type Marathi text using ISM.

### macOS
- System Preferences → Keyboard → Input Sources
- Add "Marathi - Inscript" layout
- Switch using Ctrl+Space

## Testing
Run the diagnostic script to verify font rendering:
```bash
python test_marathi_rendering.py
```

This will show available fonts and test rendering of English, Hindi, and Marathi text.

## Functionality
- The application now automatically detects the best available Indic font
- Font is properly applied to all Marathi and Hindi text
- Font information is displayed in the setup page
- All text boxes (passage box, input box, result box) use the same optimized font

## If Problems Persist

### 1. Check Font Installation
```bash
fc-list | grep -i devanagari
```

You should see at least one Devanagari font listed.

### 2. Reinstall Fonts
```bash
sudo apt install fonts-noto-devanagari
```

### 3. Clear Font Cache
```bash
fc-cache -fv
```

### 4. Check ISM Configuration
Make sure your system's input method settings have Marathi (Inscript) or Marathi (Phonetic) configured.

## Files Modified
- `app.py` - Font resolution and rendering logic
- `test_marathi_rendering.py` - Diagnostic tool (new)

## Version
Updated: March 20, 2026
