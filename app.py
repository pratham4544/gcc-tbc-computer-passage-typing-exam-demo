from __future__ import annotations

import os
import random
import sys
import time
import webbrowser
import zipfile
from dataclasses import dataclass
from xml.etree import ElementTree as ET

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QFontDatabase, QKeyEvent, QPixmap, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QBoxLayout,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


ENGLISH_PASSAGES = [
    "The school library stays open in the morning so that students can read quietly before class begins. Regular reading improves vocabulary, focus, and confidence during written and typing examinations.",
    "Typing practice becomes better when the student sits straight, keeps both hands relaxed, and presses each key with control. Speed grows slowly, but accuracy must remain the first priority in every test.",
    "A calm exam environment helps a candidate perform well under pressure. When the timer starts, the student should read the passage carefully, maintain rhythm, and avoid correcting every small mistake.",
    "Daily practice for a few minutes can create strong typing habits over time. Repeating clean and correct keystrokes is often more useful than rushing through a passage with many spelling errors.",
    "Computer based examinations require patience and concentration. Students should watch the text, use the proper finger movement, and continue typing steadily even if one difficult word appears in the passage.",
]

MARATHI_PASSAGES = [
    "मुलांनी रोज नियमित सराव केला तर टायपिंगची गती आणि अचूकता दोन्ही सुधारतात. परीक्षेमध्ये शांत मन, योग्य बसण्याची पद्धत आणि सातत्यपूर्ण टायपिंग खूप महत्त्वाचे असते.",
    "मराठी टायपिंग परीक्षेसाठी उमेदवाराने मजकूर काळजीपूर्वक वाचून मग टाइप करावा. घाईपेक्षा शुद्ध शब्द, योग्य मात्रा आणि सातत्यपूर्ण वेग अधिक महत्त्वाचा असतो.",
    "सराव करताना वेळेचे नियोजन, योग्य कीबोर्ड वापर आणि सतत लक्ष केंद्रित ठेवणे आवश्यक आहे. चांगली सवय लागली की परीक्षेत आत्मविश्वास वाढतो.",
    "ISM चालू असताना उमेदवाराने दिलेला उतारा नीट पाहून अचूक शब्द लिहिण्याचा प्रयत्न करावा. नियमित सरावामुळे चुका कमी होतात आणि गती हळूहळू वाढते.",
]

HINDI_PASSAGES = [
    "नियमित अभ्यास से टाइपिंग की गति और शुद्धता दोनों में सुधार होता है। परीक्षा के समय शांत मन, सही बैठने की मुद्रा और निरंतर अभ्यास बहुत उपयोगी साबित होता है।",
    "हिंदी टाइपिंग परीक्षा में उम्मीदवार को दिए गए गद्यांश को ध्यान से पढ़कर सही शब्दों के साथ टाइप करना चाहिए। जल्दबाजी से अधिक महत्व शुद्धता और एक समान गति का होता है।",
    "कंप्यूटर आधारित परीक्षा में सफल होने के लिए अभ्यास, धैर्य और एकाग्रता आवश्यक है। सही कुंजी प्रयोग और नियमित पुनरावृत्ति से आत्मविश्वास बढ़ता है।",
]


@dataclass(frozen=True)
class ExamProfile:
    name: str
    language: str
    duration_minutes: int | None
    target_wpm: int
    passage_key: str


PROFILES = {
    "English 30 WPM": ExamProfile("English 30 WPM", "English", 7, 30, "eng30"),
    "English 40 WPM": ExamProfile("English 40 WPM", "English", 7, 40, "eng40"),
    "Marathi 30 WPM": ExamProfile("Marathi 30 WPM", "Marathi", 7, 30, "mar30"),
    "Marathi 40 WPM": ExamProfile("Marathi 40 WPM", "Marathi", 7, 40, "mar40"),
    "Hindi 30 WPM": ExamProfile("Hindi 30 WPM", "Hindi", 7, 30, "hin30"),
    "Hindi 40 WPM": ExamProfile("Hindi 40 WPM", "Hindi", 7, 40, "hin40"),
    "Practice Without Time": ExamProfile("Practice Without Time", "English", None, 0, "practice"),
}

APP_NAMES = [
    "TypeDesk",
    "TypeSprint",
    "KeyShala",
    "TypeReady",
    "ExamKeys",
]

COMPANY_NAME = "Pushpanjali Computer Typing Institute, Dahiwadi"
COMPANY_TAGLINE = "Free typing practice software by Pushpanjali Computer Typing Institute."
COMPANY_PHONE = "9970939341"
COMPANY_BANNER_SIZE = "Recommended banner size: 800 x 150 px (PNG)"
QUESTION_PAPER_DIR = "Oct 2025 exam question paper"
TOTAL_MARKS = 40
PASS_MARKS = 16
MAX_ALLOWED_MISTAKES = 15
QUESTION_PAPER_KEYS = {
    "eng30": ["eng-30", "eng 30-speed"],
    "eng40": ["eng-40", "eng 40-speed"],
    "mar30": ["mar-30", "mar 30-speed"],
    "mar40": ["mar-40", "mar 40-speed"],
    "hin30": ["hin-30", "hin 30-speed"],
    "hin40": ["hin-40", "hin 40-speed"],
}


class TypingExamApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Typing Exam Practice")
        self._configure_window()

        self._selected_profile = "English 30 WPM"
        self._language = "English"
        self._practice_language = "English"
        self._timer_text = "07:00"
        self._page_title_text = "1. Test Setup"
        self._status_text = "Choose a test type and load a passage."
        self._font_info_text = ""

        self.current_profile = PROFILES["English 30 WPM"]
        self.current_passage = ""
        self.current_passage_label = ""
        self.active_result: dict[str, str] = {}
        self.test_running = False
        self.start_time = 0.0
        self.timer: QTimer | None = None
        self.resize_timer: QTimer | None = None

        self._register_local_nirmala()
        self.english_font_family = "Segoe UI"
        self.english_font_size = 16
        self.indic_font_family, self.indic_font_size = self._resolve_indic_font()
        self.external_passages = self._load_external_docx_passages()

        self.setup_banner_pixmap = self._load_png("img1.png")
        self.result_banner_pixmap = self._load_png("img2.png")

        self._apply_stylesheet()
        self._build_ui()
        self._update_language_mode()
        self._set_passage_for_current_selection()
        QTimer.singleShot(50, self._apply_responsive_layout)
        self._show_page("setup")

    # ── window config ──────────────────────────────────────────────

    def _configure_window(self) -> None:
        screen = QApplication.primaryScreen()
        screen_size = screen.availableSize()
        sw, sh = screen_size.width(), screen_size.height()
        width = min(1180, max(900, int(sw * 0.9)))
        height = min(760, max(620, int(sh * 0.88)))
        px = max((sw - width) // 2, 0)
        py = max((sh - height) // 2, 0)
        self.resize(width, height)
        self.move(px, py)
        self.setMinimumSize(900, 620)

    # ── stylesheet ─────────────────────────────────────────────────

    def _apply_stylesheet(self, scale: str = "normal") -> None:
        if scale == "compact":
            hero_t, hero_b = 18, 9
            sec, body, muted, val = 10, 9, 8, 11
            btn, it, iv = 9, 8, 11
            pt, st = 13, 9
        else:
            hero_t, hero_b = 21, 10
            sec, body, muted, val = 11, 10, 9, 12
            btn, it, iv = 10, 9, 13
            pt, st = 15, 10

        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background-color: #f3efe7; }}
            QFrame#hero {{ background-color: #1f3a5f; border-radius: 4px; }}
            QLabel#heroTitle {{
                color: #ffffff; font-family: "Segoe UI"; font-size: {hero_t}pt;
                font-weight: bold; background: transparent;
            }}
            QLabel#heroBody {{
                color: #d9e4f2; font-family: "Segoe UI"; font-size: {hero_b}pt;
                background: transparent;
            }}
            QLabel#pageTitle {{
                color: #183153; font-family: "Segoe UI"; font-size: {pt}pt;
                font-weight: bold; background: transparent;
            }}
            QLabel#statusText {{
                color: #52606d; font-family: "Segoe UI"; font-size: {st}pt;
                background: transparent;
            }}
            QFrame#cardFrame {{
                background-color: #fffdf8; border: 1px solid #e0ddd6; border-radius: 4px;
            }}
            QGroupBox#sectionGroup {{
                background-color: #fffdf8; border: 1px solid #d0cdc6; border-radius: 4px;
                font-family: "Segoe UI"; font-size: {sec}pt; font-weight: bold;
                color: #183153; padding-top: 16px; margin-top: 8px;
            }}
            QGroupBox#sectionGroup::title {{
                subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px;
            }}
            QLabel#bodyLabel {{
                color: #243447; font-family: "Segoe UI"; font-size: {body}pt; background: transparent;
            }}
            QLabel#mutedLabel {{
                color: #5f6b7a; font-family: "Segoe UI"; font-size: {muted}pt; background: transparent;
            }}
            QLabel#valueLabel {{
                color: #10233d; font-family: "Segoe UI"; font-size: {val}pt;
                font-weight: bold; background: transparent;
            }}
            QFrame#infoCard {{
                background-color: #eef3f8; border: 1px solid #d4dde7; border-radius: 4px;
            }}
            QLabel#infoTitle {{
                color: #5a6b7b; font-family: "Segoe UI"; font-size: {it}pt;
                font-weight: bold; background: transparent;
            }}
            QLabel#infoValue {{
                color: #17324d; font-family: "Segoe UI"; font-size: {iv}pt;
                font-weight: bold; background: transparent;
            }}
            QLabel#infoValueMono {{
                color: #17324d; font-family: "Consolas"; font-size: {iv}pt;
                font-weight: bold; background: transparent;
            }}
            QPushButton {{
                font-family: "Segoe UI"; font-size: {btn}pt; padding: 6px 16px;
                border: 1px solid #b0b8c1; border-radius: 4px; background-color: #f0ede6;
            }}
            QPushButton:hover {{ background-color: #e4e0d8; }}
            QPushButton#primaryButton {{
                font-weight: bold; background-color: #1f3a5f; color: #ffffff;
                border: 1px solid #1a3050;
            }}
            QPushButton#primaryButton:hover {{ background-color: #2a4a72; }}
            QLabel#resultTitle {{
                color: #183153; font-family: "Segoe UI"; font-size: 18pt;
                font-weight: bold; background: transparent;
            }}
            QLabel#instituteName {{
                color: #183153; font-family: "Segoe UI"; font-size: 13pt;
                font-weight: bold; background: transparent;
            }}
            QComboBox {{
                font-family: "Segoe UI"; font-size: {body}pt; padding: 4px 8px;
                border: 1px solid #b0b8c1; border-radius: 3px; background-color: #ffffff;
            }}
            QComboBox QAbstractItemView {{
                background-color: #ffffff; selection-background-color: #1f3a5f;
                selection-color: #ffffff;
            }}
            QLineEdit {{
                font-family: "Segoe UI"; font-size: {body}pt; padding: 4px 8px;
                border: 1px solid #b0b8c1; border-radius: 3px; background-color: #ffffff;
            }}
            QScrollArea {{ border: none; }}
            QScrollBar:vertical {{
                width: 12px; background-color: #f3efe7;
            }}
            QScrollBar::handle:vertical {{
                background-color: #c0bdb6; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

    # ── build UI ───────────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(18, 18, 18, 18)

        hero = QFrame()
        hero.setObjectName("hero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        ht = QLabel("Offline Typing Exam Practice")
        ht.setObjectName("heroTitle")
        hb = QLabel(
            "Windows-targeted exam simulator with English, Marathi, Hindi, "
            "and optional exam-question DOCX loading."
        )
        hb.setObjectName("heroBody")
        hero_layout.addWidget(ht)
        hero_layout.addWidget(hb)
        main_layout.addWidget(hero)

        nav = QHBoxLayout()
        nav.setContentsMargins(0, 14, 0, 8)
        self.page_title_label = QLabel(self._page_title_text)
        self.page_title_label.setObjectName("pageTitle")
        self.status_label = QLabel(self._status_text)
        self.status_label.setObjectName("statusText")
        nav.addWidget(self.page_title_label)
        nav.addStretch()
        nav.addWidget(self.status_label)
        main_layout.addLayout(nav)

        self.page_stack = QStackedWidget()
        self.page_stack.addWidget(self._build_setup_page())
        self.page_stack.addWidget(self._build_test_page())
        self.page_stack.addWidget(self._build_result_page())
        main_layout.addWidget(self.page_stack, stretch=1)

    # ── setup page ─────────────────────────────────────────────────

    def _build_setup_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        self.setup_scroll_area = QScrollArea()
        self.setup_scroll_area.setWidgetResizable(True)
        self.setup_scroll_area.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignHCenter)

        center_card = QGroupBox("Exam Setup")
        center_card.setObjectName("sectionGroup")
        center_card.setMaximumWidth(960)
        center_card.setMinimumWidth(700)
        card_layout = QGridLayout(center_card)
        card_layout.setContentsMargins(22, 28, 22, 22)
        card_layout.setColumnStretch(0, 1)
        card_layout.setColumnStretch(1, 1)

        desc = QLabel("Select exam details and start the practice test.")
        desc.setObjectName("bodyLabel")
        desc.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(desc, 0, 0, 1, 2)

        lbl_name = QLabel("Candidate Name")
        lbl_name.setObjectName("bodyLabel")
        card_layout.addWidget(lbl_name, 1, 0)
        self.candidate_name_input = QLineEdit()
        card_layout.addWidget(self.candidate_name_input, 1, 1)

        lbl_exam = QLabel("Exam Type")
        lbl_exam.setObjectName("bodyLabel")
        card_layout.addWidget(lbl_exam, 2, 0)
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(list(PROFILES.keys()))
        self.profile_combo.setCurrentText(self._selected_profile)
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        card_layout.addWidget(self.profile_combo, 2, 1)

        lbl_lang = QLabel("Language")
        lbl_lang.setObjectName("bodyLabel")
        card_layout.addWidget(lbl_lang, 3, 0)
        self.language_control = QComboBox()
        self.language_control.addItems(["English", "Marathi", "Hindi"])
        self.language_control.setEnabled(False)
        self.language_control.currentTextChanged.connect(self._on_practice_language_changed)
        card_layout.addWidget(self.language_control, 3, 1)

        lbl_time = QLabel("Time")
        lbl_time.setObjectName("bodyLabel")
        card_layout.addWidget(lbl_time, 4, 0)
        self.setup_time_label = QLabel(self._timer_text)
        self.setup_time_label.setObjectName("valueLabel")
        card_layout.addWidget(self.setup_time_label, 4, 1)

        preview_group = QGroupBox("Current Passage Preview")
        preview_group.setObjectName("sectionGroup")
        preview_layout = QVBoxLayout(preview_group)
        self.setup_preview_box = QTextEdit()
        self.setup_preview_box.setReadOnly(True)
        self.setup_preview_box.setStyleSheet("background-color: #f8fafc; border: 1px solid #ccc;")
        self.setup_preview_box.setMaximumHeight(140)
        preview_layout.addWidget(self.setup_preview_box)
        card_layout.addWidget(preview_group, 5, 0, 1, 2)

        self.font_note = QLabel(self._font_info_text)
        self.font_note.setObjectName("bodyLabel")
        self.font_note.setWordWrap(True)
        self.font_note.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.font_note, 6, 0, 1, 2)

        deva_note = QLabel(
            "Marathi and Hindi on Ubuntu need a Devanagari font. "
            "This app prefers Mangal, then Nirmala UI, then fonts such as Noto Sans Devanagari."
        )
        deva_note.setObjectName("mutedLabel")
        deva_note.setWordWrap(True)
        deva_note.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(deva_note, 7, 0, 1, 2)

        docx_note = QLabel(
            f"If present, DOCX passages are loaded automatically from: {QUESTION_PAPER_DIR}"
        )
        docx_note.setObjectName("mutedLabel")
        docx_note.setWordWrap(True)
        docx_note.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(docx_note, 8, 0, 1, 2)

        actions_layout = QHBoxLayout()
        actions_layout.setAlignment(Qt.AlignCenter)
        load_btn = QPushButton("Load Random Passage")
        load_btn.clicked.connect(self._refresh_passage)
        start_btn = QPushButton("Start Test")
        start_btn.setObjectName("primaryButton")
        start_btn.clicked.connect(self.start_test)
        actions_layout.addWidget(load_btn)
        actions_layout.addWidget(start_btn)
        card_layout.addLayout(actions_layout, 9, 0, 1, 2)

        institute_layout = QVBoxLayout()
        institute_layout.setAlignment(Qt.AlignCenter)
        inst_name = QLabel(COMPANY_NAME)
        inst_name.setObjectName("instituteName")
        inst_name.setAlignment(Qt.AlignCenter)
        institute_layout.addWidget(inst_name)
        phone_lbl = QLabel(f"Call: {COMPANY_PHONE}")
        phone_lbl.setObjectName("bodyLabel")
        phone_lbl.setAlignment(Qt.AlignCenter)
        institute_layout.addWidget(phone_lbl)
        self.setup_banner_label = QLabel()
        self.setup_banner_label.setAlignment(Qt.AlignCenter)
        self._set_banner_image(self.setup_banner_label, self.setup_banner_pixmap, "(Setup banner)")
        institute_layout.addWidget(self.setup_banner_label)
        card_layout.addLayout(institute_layout, 10, 0, 1, 2)

        scroll_layout.addWidget(center_card)
        self.setup_scroll_area.setWidget(scroll_content)
        page_layout.addWidget(self.setup_scroll_area)
        return page

    # ── test page ──────────────────────────────────────────────────

    def _build_test_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)

        self.top_bar_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.header_exam_box, self.header_exam_value = self._build_info_card("Exam Type", self._selected_profile)
        self.header_language_box, self.header_language_value = self._build_info_card("Language", self._language)
        self.header_timer_box, self.header_timer_value = self._build_info_card(
            "Time Left", self._timer_text, use_mono=True
        )
        self.top_bar_layout.addWidget(self.header_exam_box)
        self.top_bar_layout.addWidget(self.header_language_box)
        self.top_bar_layout.addWidget(self.header_timer_box)
        card_layout.addLayout(self.top_bar_layout)

        split = QHBoxLayout()

        passage_group = QGroupBox("Passage")
        passage_group.setObjectName("sectionGroup")
        passage_layout = QVBoxLayout(passage_group)
        self.passage_box = QTextEdit()
        self.passage_box.setReadOnly(True)
        self.passage_box.setStyleSheet("background-color: #f8fafc; border: 1px solid #ccc;")
        passage_layout.addWidget(self.passage_box)

        typing_group = QGroupBox("Typing Area")
        typing_group.setObjectName("sectionGroup")
        typing_layout = QVBoxLayout(typing_group)
        self.input_box = QTextEdit()
        self.input_box.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc;")
        self.input_box.setAcceptRichText(False)
        # Enable IME/ISM input for Marathi/Hindi typing via Scroll Lock
        self.input_box.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.input_box.setInputMethodHints(Qt.ImhNone)
        self.input_box.textChanged.connect(self._on_input_text_changed)
        typing_layout.addWidget(self.input_box)

        split.addWidget(passage_group)
        split.addWidget(typing_group)
        card_layout.addLayout(split, stretch=1)

        bottom = QHBoxLayout()
        back_btn = QPushButton("Back to Setup")
        back_btn.clicked.connect(self._back_to_setup)
        reset_btn = QPushButton("Reset Test")
        reset_btn.clicked.connect(self.reset_test)
        finish_btn = QPushButton("Finish Test")
        finish_btn.setObjectName("primaryButton")
        finish_btn.clicked.connect(self.finish_test)
        bottom.addWidget(back_btn)
        bottom.addStretch()
        bottom.addWidget(reset_btn)
        bottom.addWidget(finish_btn)
        card_layout.addLayout(bottom)

        page_layout.addWidget(card)
        return page

    # ── result page ────────────────────────────────────────────────

    def _build_result_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        self.result_scroll_area = QScrollArea()
        self.result_scroll_area.setWidgetResizable(True)
        self.result_scroll_area.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #fffdf8;")
        scroll_layout = QVBoxLayout(scroll_content)

        card = QFrame()
        card.setObjectName("cardFrame")
        card_grid = QGridLayout(card)
        card_grid.setContentsMargins(20, 20, 20, 20)
        card_grid.setColumnStretch(0, 1)
        card_grid.setColumnStretch(1, 1)

        title = QLabel("Result Summary")
        title.setObjectName("resultTitle")
        card_grid.addWidget(title, 0, 0, 1, 1)

        metrics_widget = QWidget()
        metrics_widget.setStyleSheet("background: transparent;")
        metrics_layout = QGridLayout(metrics_widget)
        self.result_labels: dict[str, QLabel] = {}
        labels = [
            "Candidate Name", "Exam Type", "Language", "Passage Source",
            "Elapsed Time", "Total Typed Words", "Matched Words", "Mistakes",
            "Accuracy", "Speed (WPM)", "Marks", "Target", "Result",
        ]
        for i, label_text in enumerate(labels):
            key_label = QLabel(label_text)
            key_label.setObjectName("bodyLabel")
            val_label = QLabel("-")
            val_label.setObjectName("valueLabel")
            metrics_layout.addWidget(key_label, i, 0)
            metrics_layout.addWidget(val_label, i, 1)
            self.result_labels[label_text] = val_label
        card_grid.addWidget(metrics_widget, 1, 0)

        review_group = QGroupBox("Typed Text Review")
        review_group.setObjectName("sectionGroup")
        review_layout = QVBoxLayout(review_group)
        self.result_typed_box = QTextEdit()
        self.result_typed_box.setReadOnly(True)
        self.result_typed_box.setStyleSheet("background-color: #f8fafc; border: 1px solid #ccc;")
        review_layout.addWidget(self.result_typed_box)
        card_grid.addWidget(review_group, 1, 1)

        actions_layout = QHBoxLayout()
        new_test_btn = QPushButton("New Test")
        new_test_btn.setObjectName("primaryButton")
        new_test_btn.clicked.connect(self._start_new_test_from_result)
        retry_btn = QPushButton("Retry Same Test")
        retry_btn.clicked.connect(self._retry_current_test)
        actions_layout.addWidget(new_test_btn)
        actions_layout.addWidget(retry_btn)
        actions_layout.addStretch()
        card_grid.addLayout(actions_layout, 2, 0, 1, 2)

        institute_group = QGroupBox("Institute")
        institute_group.setObjectName("sectionGroup")
        inst_layout = QVBoxLayout(institute_group)
        inst_layout.setAlignment(Qt.AlignCenter)
        self.result_banner_label = QLabel()
        self.result_banner_label.setAlignment(Qt.AlignCenter)
        self._set_banner_image(self.result_banner_label, self.result_banner_pixmap, "(Result banner)")
        inst_layout.addWidget(self.result_banner_label)
        inst_layout.addWidget(self._centered_label(COMPANY_NAME, "instituteName"))
        inst_layout.addWidget(self._centered_label(COMPANY_TAGLINE, "bodyLabel"))
        inst_layout.addWidget(self._centered_label(f"Call: {COMPANY_PHONE}", "bodyLabel"))
        inst_layout.addWidget(self._centered_label(COMPANY_BANNER_SIZE, "mutedLabel"))

        inst_actions = QHBoxLayout()
        inst_actions.setAlignment(Qt.AlignCenter)
        call_btn = QPushButton("Call Institute")
        call_btn.setObjectName("primaryButton")
        call_btn.clicked.connect(self._call_institute)
        show_btn = QPushButton("Show Number")
        show_btn.clicked.connect(self._show_phone_number)
        inst_actions.addWidget(call_btn)
        inst_actions.addWidget(show_btn)
        inst_layout.addLayout(inst_actions)
        card_grid.addWidget(institute_group, 3, 0, 1, 2)

        scroll_layout.addWidget(card)
        self.result_scroll_area.setWidget(scroll_content)
        page_layout.addWidget(self.result_scroll_area)
        return page

    # ── helpers ─────────────────────────────────────────────────────

    def _centered_label(self, text: str, object_name: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName(object_name)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        return lbl

    def _build_info_card(
        self, title: str, value: str, use_mono: bool = False
    ) -> tuple[QFrame, QLabel]:
        frame = QFrame()
        frame.setObjectName("infoCard")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("infoTitle")
        value_lbl = QLabel(value)
        if use_mono:
            value_lbl.setObjectName("infoValueMono")
        else:
            value_lbl.setObjectName("infoValue")
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        return frame, value_lbl

    # ── page navigation ────────────────────────────────────────────

    def _show_page(self, page_name: str) -> None:
        page_index = {"setup": 0, "test": 1, "result": 2}
        self.page_stack.setCurrentIndex(page_index[page_name])

        if page_name == "setup":
            self.setup_scroll_area.verticalScrollBar().setValue(0)
        if page_name == "result" and hasattr(self, "result_scroll_area"):
            self.result_scroll_area.verticalScrollBar().setValue(0)

        titles = {"setup": "1. Test Setup", "test": "2. Typing Test", "result": "3. Result"}
        self._set_page_title_text(titles[page_name])

    # ── StringVar replacement setters ──────────────────────────────

    def _set_timer_text(self, value: str) -> None:
        self._timer_text = value
        if hasattr(self, "setup_time_label"):
            self.setup_time_label.setText(value)
        if hasattr(self, "header_timer_value"):
            self.header_timer_value.setText(value)

    def _set_status_text(self, value: str) -> None:
        self._status_text = value
        if hasattr(self, "status_label"):
            self.status_label.setText(value)

    def _set_page_title_text(self, value: str) -> None:
        self._page_title_text = value
        if hasattr(self, "page_title_label"):
            self.page_title_label.setText(value)

    # ── font resolution ────────────────────────────────────────────

    def _register_local_nirmala(self) -> None:
        self._local_nirmala_registered = False
        self._local_nirmala_family = ""
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nirmala UI Regular.ttf")
        if not os.path.exists(font_path):
            return
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id >= 0:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                self._local_nirmala_family = families[0]
                self._local_nirmala_registered = True

    def _resolve_indic_font(self) -> tuple[str, int]:
        available_set = set(QFontDatabase.families())
        # Prioritize fonts with better Devanagari support
        preferred = [
            "Noto Sans Devanagari", "Noto Sans", "Nirmala UI", "Mangal",
            "Noto Serif Devanagari", "Kalimati", "Lohit Devanagari",
        ]
        for family in preferred:
            if family in available_set:
                self._font_info_text = f"Marathi font in use: {family}"
                return (family, 18)

        if self._local_nirmala_registered:
            self._font_info_text = (
                f"Marathi font in use: {self._local_nirmala_family} (from local font file)"
            )
            return (self._local_nirmala_family, 18)

        self._font_info_text = (
            "WARNING: No Indic font detected. Install 'Noto Sans Devanagari' for proper Marathi rendering. "
            "On Ubuntu: sudo apt install fonts-noto-devanagari | On Windows: Download from fonts.google.com"
        )
        return ("Sans Serif", 16)

    def _get_display_font(self, size: int | None = None) -> QFont:
        chosen_size = size or self.english_font_size
        if self._language in {"Marathi", "Hindi"}:
            font = QFont(self.indic_font_family, max(chosen_size, 13))
            # Ensure proper Devanagari text rendering with antialiasing
            font.setStyleStrategy(QFont.PreferAntialias)
            return font
        return QFont(self.english_font_family, max(chosen_size, 12))

    def _preview_font_size(self) -> int:
        width = max(self.width(), 900)
        return 11 if width < 980 else 13

    def _passage_font_size(self) -> int:
        width = max(self.width(), 900)
        height = max(self.height(), 620)
        content_length = max(len(self.current_passage), 1)
        size = 15
        if width < 1100:
            size -= 1
        if width < 980:
            size -= 1
        if height < 720:
            size -= 1
        if height < 660:
            size -= 1
        if content_length > 650:
            size -= 1
        if content_length > 950:
            size -= 1
        return max(size, 12)

    # ── responsive layout ──────────────────────────────────────────

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self.resize_timer is None:
            self.resize_timer = QTimer()
            self.resize_timer.setSingleShot(True)
            self.resize_timer.timeout.connect(self._apply_responsive_layout)
        self.resize_timer.start(120)

    def _apply_responsive_layout(self) -> None:
        w = max(self.width(), 900)
        h = max(self.height(), 620)
        scale = "compact" if (w < 980 or h < 690) else "normal"
        self._apply_stylesheet(scale)
        self._apply_header_layout()
        self._sync_custom_font()

    def _apply_header_layout(self) -> None:
        if not hasattr(self, "top_bar_layout"):
            return
        width = max(self.width(), 900)
        if width < 980:
            self.top_bar_layout.setDirection(QBoxLayout.TopToBottom)
        else:
            self.top_bar_layout.setDirection(QBoxLayout.LeftToRight)

    # ── passage management ─────────────────────────────────────────

    def _on_profile_changed(self, text: str) -> None:
        self._selected_profile = text
        self.current_profile = PROFILES[text]
        self._update_language_mode()
        self._set_time_text()
        self._sync_custom_font()
        self._set_passage_for_current_selection()
        self._set_status_text("Test configuration updated.")

    def _on_practice_language_changed(self, text: str) -> None:
        if self.current_profile.duration_minutes is None:
            self._practice_language = text
            self._language = text
            self._sync_custom_font()
            self._set_passage_for_current_selection()
            self._set_status_text("Practice language changed.")

    def _update_language_mode(self) -> None:
        if self.current_profile.duration_minutes is None:
            self.language_control.setEnabled(True)
            self._language = self._practice_language
        else:
            self.language_control.setEnabled(False)
            self._language = self.current_profile.language

    def _sync_custom_font(self) -> None:
        if hasattr(self, "passage_box"):
            self._render_passages()
        if hasattr(self, "input_box"):
            self._apply_typing_fonts()
        if hasattr(self, "font_note"):
            self.font_note.setText(self._font_info_text)
        if hasattr(self, "result_typed_box") and self.active_result:
            if self.page_stack.currentIndex() == 2:
                self._show_result_page()

    def _set_time_text(self) -> None:
        if self.current_profile.duration_minutes is None:
            self._set_timer_text("No Limit")
        else:
            self._set_timer_text(f"{self.current_profile.duration_minutes:02d}:00")

    def _set_passage_for_current_selection(self) -> None:
        selected_profile = PROFILES[self._selected_profile]
        passage_key = selected_profile.passage_key

        if passage_key in self.external_passages and self.external_passages[passage_key]:
            picked = random.choice(self.external_passages[passage_key])
            self.current_passage = picked["text"]
            self.current_passage_label = picked["label"]
        else:
            self.current_passage = self._pick_builtin_passage(self._language)
            self.current_passage_label = "Built-in passage"

        self._render_passages()

    def _render_passages(self) -> None:
        font = self._get_display_font(self._passage_font_size())
        display_text = self._format_passage_for_display(self.current_passage)

        if hasattr(self, "passage_box"):
            self.passage_box.setFont(font)
            self.passage_box.setPlainText(display_text)

        self._update_preview_box()

    def _update_preview_box(self) -> None:
        if not hasattr(self, "setup_preview_box"):
            return
        font = self._get_display_font(self._preview_font_size())
        self.setup_preview_box.setFont(font)
        self.setup_preview_box.setPlainText(
            self._format_passage_for_display(self.current_passage)
        )

    def _refresh_passage(self) -> None:
        if self.test_running:
            QMessageBox.information(self, "Test Running", "Finish or reset the current test first.")
            return
        self._set_passage_for_current_selection()
        self._set_status_text(f"Passage ready. Source: {self.current_passage_label}")

    def _apply_typing_fonts(self) -> None:
        font = self._get_display_font(self._passage_font_size())
        self.passage_box.setFont(font)
        self.input_box.setFont(font)
        self.result_typed_box.setFont(font)

    # ── test flow ──────────────────────────────────────────────────

    def start_test(self) -> None:
        if self.test_running:
            return

        self.current_profile = PROFILES[self._selected_profile]
        self._update_language_mode()
        self._sync_custom_font()
        self._set_passage_for_current_selection()

        candidate_name = self.candidate_name_input.text().strip()
        if not candidate_name:
            QMessageBox.warning(self, "Candidate Name", "Please enter candidate name.")
            return

        if not self.current_passage.strip():
            QMessageBox.warning(self, "No Passage", "Please load a passage before starting.")
            return

        self.input_box.clear()
        self._apply_typing_fonts()

        if hasattr(self, "header_exam_value"):
            self.header_exam_value.setText(self._selected_profile)
        if hasattr(self, "header_language_value"):
            self.header_language_value.setText(self._language)

        self.test_running = True
        self.start_time = time.time()
        self._set_time_text()
        if self._language in {"Marathi", "Hindi"}:
            self._set_status_text(
                "Test is running. Enable ISM (Scroll Lock) to type in "
                f"{self._language}."
            )
        else:
            self._set_status_text("Test is running.")
        self._show_page("test")
        self._ensure_ime_enabled()
        self.input_box.setFocus()

        if self.current_profile.duration_minutes is not None:
            self._schedule_timer()

    def _schedule_timer(self) -> None:
        if self.timer is not None:
            self.timer.stop()
        self.timer = QTimer()
        self.timer.setInterval(250)
        self.timer.timeout.connect(self._tick_timer)
        self.timer.start()

    def _tick_timer(self) -> None:
        if not self.test_running or self.current_profile.duration_minutes is None:
            if self.timer is not None:
                self.timer.stop()
            return

        total_seconds = self.current_profile.duration_minutes * 60
        elapsed_seconds = int(time.time() - self.start_time)
        remaining = max(0, total_seconds - elapsed_seconds)
        minutes, seconds = divmod(remaining, 60)
        self._set_timer_text(f"{minutes:02d}:{seconds:02d}")

        if remaining == 0:
            self.timer.stop()
            self.finish_test(time_up=True)

    def finish_test(self, time_up: bool = False) -> None:
        if not self.test_running:
            self._set_status_text("No running test to finish.")
            return

        if self.timer is not None:
            self.timer.stop()
            self.timer = None

        self.test_running = False
        elapsed = max(time.time() - self.start_time, 1)
        self._calculate_results(elapsed)
        self._show_result_page()

        if time_up:
            QMessageBox.information(self, "Time Up", "Time is over!")
            self._set_status_text("Time is over. Result calculated.")
        else:
            self._set_status_text("Test finished. Result calculated.")

    def reset_test(self) -> None:
        if self.timer is not None:
            self.timer.stop()
            self.timer = None

        self.test_running = False
        self.input_box.clear()
        self._set_time_text()
        self._set_status_text("Current test reset.")

    def _back_to_setup(self) -> None:
        if self.test_running:
            reply = QMessageBox.question(
                self,
                "Leave Test",
                "The current test is running. Do you want to stop it and return to setup?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            self.reset_test()
        self._show_page("setup")
        self._set_status_text("Back on setup page.")

    # ── results ────────────────────────────────────────────────────

    def _calculate_results(self, elapsed_seconds: float) -> None:
        source_words = self._tokenize(self.current_passage)
        typed_text = self.input_box.toPlainText().strip()
        typed_words = self._tokenize(typed_text)

        matched_words = sum(
            1 for expected, actual in zip(source_words, typed_words) if expected == actual
        )
        total_typed = len(typed_words)
        mistakes = max(total_typed - matched_words, 0)
        accuracy = (matched_words / total_typed * 100) if total_typed else 0.0
        elapsed_minutes = elapsed_seconds / 60
        speed_wpm = (matched_words / elapsed_minutes) if elapsed_minutes else 0.0

        target = (
            f"{self.current_profile.target_wpm} WPM"
            if self.current_profile.target_wpm
            else "Practice"
        )
        marks = self._calculate_marks(matched_words)
        result_text = self._calculate_result(marks, mistakes)

        self.active_result = {
            "Candidate Name": self.candidate_name_input.text().strip(),
            "Exam Type": self.current_profile.name,
            "Language": self._language,
            "Passage Source": self.current_passage_label,
            "Elapsed Time": self._format_elapsed(elapsed_seconds),
            "Total Typed Words": str(total_typed),
            "Matched Words": str(matched_words),
            "Mistakes": str(mistakes),
            "Accuracy": f"{accuracy:.2f}%",
            "Speed (WPM)": f"{speed_wpm:.2f}",
            "Marks": f"{marks}/{TOTAL_MARKS}",
            "Target": target,
            "Result": result_text,
            "Typed Text": typed_text,
        }

    def _show_result_page(self) -> None:
        self._show_page("result")
        for label, widget in self.result_labels.items():
            widget.setText(self.active_result.get(label, "-"))

        font = self._get_display_font(self._passage_font_size())
        self.result_typed_box.setFont(font)
        self.result_typed_box.setPlainText(self.active_result.get("Typed Text", ""))

    # ── input monitoring ───────────────────────────────────────────

    def _on_input_text_changed(self) -> None:
        if self._language not in {"Marathi", "Hindi"}:
            return
        typed_text = self.input_box.toPlainText()
        if typed_text and set(typed_text.replace(" ", "").replace("\n", "")) <= {"?"}:
            self._set_status_text(
                "ISM is sending '?' -- switch ISM to Unicode mode, or use Windows "
                "Marathi/Hindi keyboard (Settings > Language) instead of legacy ISM."
            )

    def _ensure_ime_enabled(self) -> None:
        """Re-enable IME on the input box (call before focusing for Marathi/Hindi)."""
        self.input_box.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.input_box.setInputMethodHints(Qt.ImhNone)

    # ── business logic (unchanged) ─────────────────────────────────

    def _pick_builtin_passage(self, language: str) -> str:
        if language == "Marathi":
            return random.choice(MARATHI_PASSAGES)
        if language == "Hindi":
            return random.choice(HINDI_PASSAGES)
        return random.choice(ENGLISH_PASSAGES)

    def _format_passage_for_display(self, text: str) -> str:
        normalized = text.replace("\r\n", "\n")
        lines = normalized.split("\n")
        for index, line in enumerate(lines):
            if line.strip():
                if not line.startswith("\t"):
                    lines[index] = f"\t{line}"
                break
        return "\n".join(lines)

    def _calculate_marks(self, matched_words: int) -> int:
        if self.current_profile.duration_minutes is None or self.current_profile.target_wpm == 0:
            return 0
        target_words = self.current_profile.target_wpm * self.current_profile.duration_minutes
        if target_words <= 0:
            return 0
        marks = round((matched_words / target_words) * TOTAL_MARKS)
        return max(0, min(TOTAL_MARKS, marks))

    def _calculate_result(self, marks: int, mistakes: int) -> str:
        if self.current_profile.duration_minutes is None:
            return "Practice"
        if marks >= PASS_MARKS and mistakes <= MAX_ALLOWED_MISTAKES:
            return "Pass"
        return "Fail"

    def _load_external_docx_passages(self) -> dict[str, list[dict[str, str]]]:
        root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), QUESTION_PAPER_DIR)
        loaded: dict[str, list[dict[str, str]]] = {key: [] for key in QUESTION_PAPER_KEYS}
        if not os.path.isdir(root_dir):
            return loaded

        for dirpath, _, filenames in os.walk(root_dir):
            normalized_path = dirpath.lower().replace("_", " ")
            for filename in filenames:
                if not filename.lower().endswith(".docx"):
                    continue
                passage_key = self._match_passage_key(normalized_path)
                if passage_key is None:
                    continue
                file_path = os.path.join(dirpath, filename)
                text = self._extract_docx_text(file_path)
                if not text:
                    continue
                loaded[passage_key].append(
                    {
                        "label": filename,
                        "text": text,
                    }
                )
        return loaded

    def _match_passage_key(self, normalized_path: str) -> str | None:
        for passage_key, markers in QUESTION_PAPER_KEYS.items():
            if all(marker in normalized_path for marker in markers):
                return passage_key
        return None

    def _extract_docx_text(self, file_path: str) -> str:
        try:
            with zipfile.ZipFile(file_path) as archive:
                document_xml = archive.read("word/document.xml")
        except (KeyError, FileNotFoundError, zipfile.BadZipFile, OSError):
            return ""

        try:
            root = ET.fromstring(document_xml)
        except ET.ParseError:
            return ""

        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs: list[str] = []
        for paragraph in root.findall(".//w:p", namespace):
            parts = []
            for node in paragraph.iter():
                if node.tag.endswith("}t") and node.text:
                    parts.append(node.text)
                elif node.tag.endswith("}tab"):
                    parts.append("\t")
            line = "".join(parts).replace("\xa0", " ").rstrip()
            if line.strip():
                paragraphs.append(line)

        return "\n".join(paragraphs).strip("\n")

    # ── image loading ──────────────────────────────────────────────

    def _load_png(self, file_name: str) -> QPixmap | None:
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
        if not os.path.exists(image_path):
            return None
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return None
        return pixmap

    def _set_banner_image(self, label: QLabel, pixmap: QPixmap | None, fallback_text: str) -> None:
        if pixmap is not None:
            label.setPixmap(pixmap)
            label.setStyleSheet(
                "border: 1px solid #ccc; padding: 6px; background-color: #fffdf8;"
            )
        else:
            label.setText(fallback_text)
            label.setStyleSheet(
                "font-family: 'Segoe UI'; font-size: 11pt; font-weight: bold; "
                "color: #183153; padding: 20px; border: 1px solid #ccc; "
                "background-color: #fffdf8;"
            )

    # ── institute actions ──────────────────────────────────────────

    def _show_phone_number(self) -> None:
        QMessageBox.information(self, "Institute Contact", f"{COMPANY_NAME}\nCall: {COMPANY_PHONE}")

    def _call_institute(self) -> None:
        try:
            webbrowser.open(f"tel:{COMPANY_PHONE}")
        except Exception:
            self._show_phone_number()

    # ── navigation helpers ─────────────────────────────────────────

    def _start_new_test_from_result(self) -> None:
        self.input_box.clear()
        self._show_page("setup")
        self._set_status_text("Ready for a new test.")

    def _retry_current_test(self) -> None:
        self.input_box.clear()
        self._show_page("test")
        self.start_test()

    # ── static helpers ─────────────────────────────────────────────

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        cleaned = text.replace("\n", " ").split()
        return [word.strip(".,!?;:\"'()[]{}") for word in cleaned if word.strip()]

    @staticmethod
    def _format_elapsed(elapsed_seconds: float) -> str:
        total_seconds = int(elapsed_seconds)
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"


def main() -> None:
    app = QApplication(sys.argv)
    window = TypingExamApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
