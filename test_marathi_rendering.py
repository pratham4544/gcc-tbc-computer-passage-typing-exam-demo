#!/usr/bin/env python3
"""Diagnostic script to test Marathi font rendering in PySide6"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtGui import QFont, QFontDatabase

def test_marathi_fonts():
    app = QApplication(sys.argv)
    
    # Check available fonts
    print("=" * 60)
    print("Available Devanagari/Indic-related fonts:")
    print("=" * 60)
    all_fonts = QFontDatabase.families()
    devanagari_fonts = [f for f in all_fonts if any(x in f.lower() for x in 
                       ['devanagari', 'noto', 'nirmala', 'mangal', 'kalimati', 'lohit'])]
    
    if devanagari_fonts:
        for font in sorted(devanagari_fonts):
            print(f"  ✓ {font}")
    else:
        print("  ✗ No Devanagari fonts found!")
        print("\n  Recommended fonts to install:")
        print("  - Ubuntu/Debian: sudo apt install fonts-noto-devanagari")
        print("  - Fedora: sudo dnf install google-noto-sans-devanagari-fonts")
        print("  - macOS: brew install font-noto-sans-devanagari")
        print("  - Windows: Download from https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari")
    
    # Test rendering
    window = QWidget()
    window.setWindowTitle("Marathi Font Rendering Test")
    window.setGeometry(100, 100, 600, 400)
    
    layout = QVBoxLayout()
    
    # Test text in Marathi (Devanagari script)
    test_passages = {
        "Marathi": "मुलांनी रोज नियमित सराव केला तर टायपिंगची गती आणि अचूकता दोन्ही सुधारतात.",
        "Hindi": "नियमित अभ्यास से टाइपिंग की गति और शुद्धता दोनों में सुधार होता है।",
        "English": "Typing practice improves both speed and accuracy."
    }
    
    print("\n" + "=" * 60)
    print("Testing font rendering:")
    print("=" * 60)
    
    for language, text in test_passages.items():
        label = QLabel(f"{language}:")
        layout.addWidget(label)
        
        # Try each font
        font_families_to_try = [
            "Noto Sans Devanagari", "Noto Sans", "Nirmala UI", "Mangal", 
            "Lohit Devanagari", "Kalimati"
        ]
        
        test_box = QTextEdit()
        test_box.setPlainText(text)
        test_box.setReadOnly(True)
        test_box.setMaximumHeight(60)
        
        font_found = False
        for font_family in font_families_to_try:
            if font_family in all_fonts:
                font = QFont(font_family, 14)
                font.setStyleStrategy(QFont.PreferAntialias)
                test_box.setFont(font)
                test_box.setToolTip(f"Using: {font_family}")
                print(f"  {language}: Using {font_family}")
                font_found = True
                break
        
        if not font_found:
            print(f"  {language}: ✗ No suitable font found! Rendering may look incorrect.")
        
        layout.addWidget(test_box)
        layout.addSpacing(10)
    
    print("\n" + "=" * 60)
    print("If Marathi/Hindi text appears garbled, install Noto Sans Devanagari.")
    print("=" * 60 + "\n")
    
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    test_marathi_fonts()
