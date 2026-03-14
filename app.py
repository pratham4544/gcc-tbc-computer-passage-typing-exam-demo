import os
import random
import sys
import time
import tkinter as tk
import webbrowser
import zipfile
from dataclasses import dataclass
from tkinter import font as tkfont
from tkinter import messagebox, ttk
from xml.etree import ElementTree as ET


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
COMPANY_BANNER_SIZE = "Recommended banner size: 1200 x 300 px"
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


class TypingExamApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Typing Exam Practice")
        self._configure_window()
        self.root.configure(bg="#f3efe7")
        self._enable_input_methods()

        self.selected_profile = tk.StringVar(value="English 30 WPM")
        self.candidate_name_var = tk.StringVar()
        self.language_var = tk.StringVar(value="English")
        self.practice_language_var = tk.StringVar(value="English")
        self.timer_text = tk.StringVar(value="07:00")
        self.page_title_text = tk.StringVar(value="1. Test Setup")
        self.status_text = tk.StringVar(value="Choose a test type and load a passage.")
        self.font_info_text = tk.StringVar(value="")

        self.current_profile = PROFILES["English 30 WPM"]
        self.current_passage = ""
        self.current_passage_label = ""
        self.active_result: dict[str, str] = {}
        self.test_running = False
        self.start_time = 0.0
        self.timer_job: str | None = None
        self.resize_job: str | None = None
        self.local_nirmala_registered = self._try_register_local_nirmala()
        self.setup_banner_image = self._load_png("img1.png")
        self.result_banner_image = self._load_png("img2.png")
        self.setup_canvas: tk.Canvas | None = None
        self.setup_scroll_body: ttk.Frame | None = None
        self.split_frame: ttk.Frame | None = None
        self.top_bar: ttk.Frame | None = None

        self.english_font_family = "Segoe UI"
        self.english_font_size = 16
        self.indic_font_family, self.indic_font_size = self._resolve_indic_font()
        self.english_font = (self.english_font_family, self.english_font_size)
        self.indic_font = (self.indic_font_family, self.indic_font_size)
        self.external_passages = self._load_external_docx_passages()

        self._configure_styles()
        self._build_ui()
        self._update_language_mode()
        self._set_passage_for_current_selection()
        self.root.bind("<Configure>", self._on_window_resized)
        self.root.after(50, self._apply_responsive_layout)
        self._show_page("setup")

    def _configure_window(self) -> None:
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = min(1180, max(900, int(screen_width * 0.9)))
        height = min(760, max(620, int(screen_height * 0.88)))
        pos_x = max((screen_width - width) // 2, 0)
        pos_y = max((screen_height - height) // 2, 0)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        self.root.minsize(900, 620)

    def _configure_styles(self) -> None:
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        if "clam" in available_themes:
            self.style.theme_use("clam")

        self.style.configure("App.TFrame", background="#f3efe7")
        self.style.configure("Card.TFrame", background="#fffdf8")
        self.style.configure("Hero.TFrame", background="#1f3a5f")
        self.style.configure("Section.TLabelframe", background="#fffdf8", borderwidth=1)
        self.style.configure("InfoCard.TFrame", background="#eef3f8")
        self._apply_style_scale()

    def _build_ui(self) -> None:
        shell = ttk.Frame(self.root, style="App.TFrame", padding=18)
        shell.pack(fill="both", expand=True)

        hero = ttk.Frame(shell, style="Hero.TFrame", padding=(20, 18))
        hero.pack(fill="x")
        ttk.Label(hero, text="Offline Typing Exam Practice", style="HeroTitle.TLabel").pack(anchor="w")
        ttk.Label(
            hero,
            text="Windows-targeted exam simulator with English, Marathi, Hindi, and optional exam-question DOCX loading.",
            style="HeroBody.TLabel",
        ).pack(anchor="w", pady=(6, 0))

        nav = ttk.Frame(shell, style="App.TFrame", padding=(0, 14, 0, 8))
        nav.pack(fill="x")
        self.page_title_label = tk.Label(
            nav,
            textvariable=self.page_title_text,
            font=("Segoe UI", 15, "bold"),
            bg="#f3efe7",
            fg="#183153",
        )
        self.page_title_label.pack(side="left")
        self.status_label = tk.Label(nav, textvariable=self.status_text, bg="#f3efe7", fg="#52606d")
        self.status_label.pack(side="right")

        self.page_host = ttk.Frame(shell, style="App.TFrame")
        self.page_host.pack(fill="both", expand=True)

        self.pages: dict[str, ttk.Frame] = {}
        self.pages["setup"] = self._build_setup_page()
        self.pages["test"] = self._build_test_page()
        self.pages["result"] = self._build_result_page()

    def _build_setup_page(self) -> ttk.Frame:
        page = ttk.Frame(self.page_host, style="App.TFrame")

        layout = ttk.Frame(page, style="App.TFrame")
        layout.pack(fill="both", expand=True)
        layout.columnconfigure(0, weight=1)
        layout.rowconfigure(0, weight=1)

        canvas = tk.Canvas(layout, bg="#f3efe7", highlightthickness=0, borderwidth=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(layout, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        scroll_body = ttk.Frame(canvas, style="App.TFrame")
        canvas_window = canvas.create_window((0, 0), window=scroll_body, anchor="n")

        def _sync_setup_scroll_region(_event=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            if canvas_width > 0:
                canvas.itemconfigure(canvas_window, width=canvas_width)

        def _resize_setup_card(_event) -> None:
            width = min(max(_event.width - 48, 760), 960)
            center_card.configure(width=width)

        def _on_setup_mousewheel(event) -> str | None:
            if not page.winfo_ismapped():
                return None
            delta = event.delta
            if delta == 0 and getattr(event, "num", None) in (4, 5):
                delta = 120 if event.num == 4 else -120
            if delta:
                canvas.yview_scroll(int(-delta / 120), "units")
                return "break"
            return None

        scroll_body.bind("<Configure>", _sync_setup_scroll_region)
        canvas.bind("<Configure>", _resize_setup_card)
        canvas.bind_all("<MouseWheel>", _on_setup_mousewheel)
        canvas.bind_all("<Button-4>", _on_setup_mousewheel)
        canvas.bind_all("<Button-5>", _on_setup_mousewheel)

        self.setup_canvas = canvas
        self.setup_scroll_body = scroll_body

        center_card = ttk.LabelFrame(scroll_body, text="Exam Setup", style="Section.TLabelframe", padding=22)
        center_card.pack(fill="x", expand=True, padx=24, pady=18)
        center_card.columnconfigure(0, weight=1)
        center_card.columnconfigure(1, weight=1)

        ttk.Label(
            center_card,
            text="Select exam details and start the practice test.",
            style="Body.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="n", pady=(0, 16))

        ttk.Label(center_card, text="Candidate Name", style="Body.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Entry(center_card, textvariable=self.candidate_name_var, width=32).grid(
            row=1, column=1, sticky="ew", padx=(14, 0), pady=(0, 12)
        )

        ttk.Label(center_card, text="Exam Type", style="Body.TLabel").grid(row=2, column=0, sticky="w")
        profile_menu = ttk.Combobox(
            center_card,
            textvariable=self.selected_profile,
            state="readonly",
            values=list(PROFILES.keys()),
            width=30,
        )
        profile_menu.grid(row=2, column=1, sticky="ew", padx=(14, 0), pady=(0, 12))
        profile_menu.bind("<<ComboboxSelected>>", self._on_profile_changed)

        ttk.Label(center_card, text="Language", style="Body.TLabel").grid(row=3, column=0, sticky="w")
        self.language_control = ttk.Combobox(
            center_card,
            textvariable=self.practice_language_var,
            state="disabled",
            values=["English", "Marathi", "Hindi"],
            width=18,
        )
        self.language_control.grid(row=3, column=1, sticky="w", padx=(14, 0), pady=(0, 12))
        self.language_control.bind("<<ComboboxSelected>>", self._on_practice_language_changed)

        ttk.Label(center_card, text="Time", style="Body.TLabel").grid(row=4, column=0, sticky="w")
        self.setup_time_label = ttk.Label(center_card, textvariable=self.timer_text, style="Value.TLabel")
        self.setup_time_label.grid(row=4, column=1, sticky="w", padx=(14, 0), pady=(0, 12))

        preview_frame = ttk.LabelFrame(center_card, text="Current Passage Preview", style="Section.TLabelframe", padding=12)
        preview_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(4, 14))
        self.setup_preview_box = tk.Text(
            preview_frame,
            wrap="word",
            height=8,
            font=self.english_font,
            padx=10,
            pady=10,
            relief="solid",
            borderwidth=1,
            background="#f8fafc",
            state="disabled",
            width=70,
        )
        self.setup_preview_box.pack(fill="both", expand=True)

        self.font_note = ttk.Label(
            center_card,
            textvariable=self.font_info_text,
            style="Body.TLabel",
            wraplength=620,
            justify="center",
        )
        self.font_note.grid(row=6, column=0, columnspan=2, sticky="n", pady=(0, 6))

        ttk.Label(
            center_card,
            text=(
                "Marathi and Hindi on Ubuntu need a Devanagari font. This app prefers Mangal, then Nirmala UI, then fonts such as Noto Sans Devanagari."
            ),
            style="Muted.TLabel",
            wraplength=620,
            justify="center",
        ).grid(row=7, column=0, columnspan=2, sticky="n", pady=(0, 12))

        ttk.Label(
            center_card,
            text=f"If present, DOCX passages are loaded automatically from: {QUESTION_PAPER_DIR}",
            style="Muted.TLabel",
            wraplength=620,
            justify="center",
        ).grid(row=8, column=0, columnspan=2, sticky="n", pady=(0, 12))

        actions = ttk.Frame(center_card, style="Card.TFrame")
        actions.grid(row=9, column=0, columnspan=2, pady=(4, 14))
        ttk.Button(actions, text="Load Random Passage", command=self._refresh_passage).pack(side="left")
        ttk.Button(actions, text="Start Test", style="Primary.TButton", command=self.start_test).pack(side="left", padx=(12, 0))

        institute_box = ttk.Frame(center_card, style="Card.TFrame")
        institute_box.grid(row=10, column=0, columnspan=2, sticky="ew")
        institute_box.columnconfigure(0, weight=1)
        tk.Label(
            institute_box,
            text=COMPANY_NAME,
            font=("Segoe UI", 13, "bold"),
            bg="#fffdf8",
            fg="#183153",
        ).grid(row=0, column=0, pady=(0, 6))
        ttk.Label(institute_box, text=f"Call: {COMPANY_PHONE}", style="Body.TLabel").grid(row=1, column=0, pady=(0, 10))
        self.setup_banner_label = tk.Label(institute_box, bg="#fffdf8")
        self.setup_banner_label.grid(row=2, column=0)
        self._set_banner_image(self.setup_banner_label, self.setup_banner_image, "(Setup banner)")

        return page

    def _build_test_page(self) -> ttk.Frame:
        page = ttk.Frame(self.page_host, style="App.TFrame")

        card = ttk.Frame(page, style="Card.TFrame", padding=16)
        card.pack(fill="both", expand=True)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        top_bar = ttk.Frame(card, style="Card.TFrame")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        top_bar.columnconfigure((0, 1, 2), weight=1)
        self.top_bar = top_bar

        self.header_exam_box = self._build_info_card(top_bar, "Exam Type", self.selected_profile)
        self.header_exam_box.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.header_language_box = self._build_info_card(top_bar, "Language", self.language_var)
        self.header_language_box.grid(row=0, column=1, sticky="ew", padx=4)
        self.header_timer_box = self._build_info_card(top_bar, "Time Left", self.timer_text, use_mono=True)
        self.header_timer_box.grid(row=0, column=2, sticky="ew", padx=(8, 0))

        split = ttk.Frame(card, style="Card.TFrame")
        split.grid(row=1, column=0, sticky="nsew")
        split.columnconfigure(0, weight=1)
        split.columnconfigure(1, weight=1)
        split.rowconfigure(0, weight=1)
        self.split_frame = split

        passage_card = ttk.LabelFrame(split, text="Passage", style="Section.TLabelframe", padding=12)
        passage_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        passage_card.rowconfigure(0, weight=1)
        passage_card.columnconfigure(0, weight=1)

        self.passage_box = tk.Text(
            passage_card,
            wrap="word",
            font=self.english_font,
            padx=12,
            pady=12,
            relief="solid",
            borderwidth=1,
            background="#f8fafc",
            state="disabled",
            width=46,
        )
        self.passage_box.grid(row=0, column=0, sticky="nsew")

        typing_card = ttk.LabelFrame(split, text="Typing Area", style="Section.TLabelframe", padding=12)
        typing_card.grid(row=0, column=1, sticky="nsew")
        typing_card.rowconfigure(0, weight=1)
        typing_card.columnconfigure(0, weight=1)

        self.input_box = tk.Text(
            typing_card,
            wrap="word",
            font=self.english_font,
            padx=12,
            pady=12,
            relief="solid",
            borderwidth=1,
            background="#ffffff",
            undo=True,
            width=46,
        )
        self.input_box.grid(row=0, column=0, sticky="nsew")
        self.input_box.bind("<KeyRelease>", self._on_input_key_release)

        bottom_bar = ttk.Frame(card, style="Card.TFrame")
        bottom_bar.grid(row=2, column=0, sticky="ew", pady=(14, 0))

        ttk.Button(bottom_bar, text="Back to Setup", command=self._back_to_setup).pack(side="left")
        ttk.Button(bottom_bar, text="Finish Test", style="Primary.TButton", command=self.finish_test).pack(side="right")
        ttk.Button(bottom_bar, text="Reset Test", command=self.reset_test).pack(side="right", padx=(0, 10))

        return page

    def _build_result_page(self) -> ttk.Frame:
        page = ttk.Frame(self.page_host, style="App.TFrame")

        card = ttk.Frame(page, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        tk.Label(
            card,
            text="Result Summary",
            font=("Segoe UI", 18, "bold"),
            bg="#fffdf8",
            fg="#183153",
        ).grid(row=0, column=0, sticky="w", pady=(0, 16))

        metrics = ttk.Frame(card, style="Card.TFrame")
        metrics.grid(row=1, column=0, sticky="nw")

        self.result_labels: dict[str, ttk.Label] = {}
        labels = [
            "Candidate Name",
            "Exam Type",
            "Language",
            "Passage Source",
            "Elapsed Time",
            "Total Typed Words",
            "Matched Words",
            "Mistakes",
            "Accuracy",
            "Speed (WPM)",
            "Marks",
            "Target",
            "Result",
        ]
        for index, label in enumerate(labels):
            ttk.Label(metrics, text=label, style="Body.TLabel").grid(row=index, column=0, sticky="w", pady=5)
            value = ttk.Label(metrics, text="-", style="Value.TLabel")
            value.grid(row=index, column=1, sticky="w", padx=(16, 0), pady=5)
            self.result_labels[label] = value

        note_frame = ttk.LabelFrame(card, text="Typed Text Review", style="Section.TLabelframe", padding=12)
        note_frame.grid(row=1, column=1, sticky="nsew", padx=(24, 0))
        note_frame.rowconfigure(0, weight=1)
        note_frame.columnconfigure(0, weight=1)

        self.result_typed_box = tk.Text(
            note_frame,
            wrap="word",
            font=self.english_font,
            padx=10,
            pady=10,
            relief="solid",
            borderwidth=1,
            background="#f8fafc",
            state="disabled",
            height=18,
        )
        self.result_typed_box.grid(row=0, column=0, sticky="nsew")

        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=2, column=0, columnspan=2, sticky="w", pady=(20, 0))
        ttk.Button(actions, text="New Test", style="Primary.TButton", command=self._start_new_test_from_result).pack(side="left")
        ttk.Button(actions, text="Retry Same Test", command=self._retry_current_test).pack(side="left", padx=(10, 0))

        ad_frame = ttk.LabelFrame(card, text="Institute", style="Section.TLabelframe", padding=18)
        ad_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        ad_frame.columnconfigure(0, weight=1)

        ad_inner = ttk.Frame(ad_frame, style="Card.TFrame")
        ad_inner.grid(row=0, column=0, sticky="", pady=(4, 2))
        ad_inner.columnconfigure(0, weight=1)

        self.result_banner_label = tk.Label(ad_inner, bg="#fffdf8")
        self.result_banner_label.grid(row=0, column=0, pady=(0, 18))
        self._set_banner_image(self.result_banner_label, self.result_banner_image, "(Result banner)")

        tk.Label(
            ad_inner,
            text=COMPANY_NAME,
            font=("Segoe UI", 15, "bold"),
            bg="#fffdf8",
            fg="#183153",
        ).grid(row=1, column=0, pady=(0, 6))
        ttk.Label(ad_inner, text=COMPANY_TAGLINE, style="Body.TLabel", justify="center").grid(row=2, column=0, pady=(0, 4))
        ttk.Label(ad_inner, text=f"Call: {COMPANY_PHONE}", style="Body.TLabel", justify="center").grid(row=3, column=0, pady=(0, 4))
        ttk.Label(ad_inner, text=COMPANY_BANNER_SIZE, style="Muted.TLabel", justify="center").grid(row=4, column=0, pady=(0, 12))

        ad_actions = ttk.Frame(ad_inner, style="Card.TFrame")
        ad_actions.grid(row=5, column=0)
        ttk.Button(ad_actions, text="Call Institute", style="Primary.TButton", command=self._call_institute).pack(side="left")
        ttk.Button(ad_actions, text="Show Number", command=self._show_phone_number).pack(side="left", padx=(10, 0))

        return page

    def _show_page(self, page_name: str) -> None:
        for name, frame in self.pages.items():
            if name == page_name:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

        if page_name == "setup" and self.setup_canvas is not None:
            self.setup_canvas.yview_moveto(0)

        titles = {
            "setup": "1. Test Setup",
            "test": "2. Typing Test",
            "result": "3. Result",
        }
        self.page_title_text.set(titles[page_name])

    def _build_info_card(
        self,
        parent: ttk.Frame,
        title: str,
        value_var: tk.StringVar,
        use_mono: bool = False,
    ) -> ttk.Frame:
        card = ttk.Frame(parent, style="InfoCard.TFrame", padding=(14, 10))
        ttk.Label(card, text=title, style="InfoTitle.TLabel").pack(anchor="w")
        if use_mono:
            value = tk.Label(
                card,
                textvariable=value_var,
                font=("Consolas", 16, "bold"),
                bg="#eef3f8",
                fg="#17324d",
            )
            value.pack(anchor="w", pady=(4, 0))
        else:
            ttk.Label(card, textvariable=value_var, style="InfoValue.TLabel").pack(anchor="w", pady=(4, 0))
        return card

    def _enable_input_methods(self) -> None:
        try:
            self.root.tk.call("tk", "useinputmethods", True)
        except tk.TclError:
            pass

    def _try_register_local_nirmala(self) -> bool:
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nirmala UI Regular.ttf")
        if not os.path.exists(font_path):
            return False

        if sys.platform.startswith("win"):
            try:
                import ctypes

                FR_PRIVATE = 0x10
                added = ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
                return added > 0
            except Exception:
                return False

        return False

    def _resolve_indic_font(self) -> tuple[str, int]:
        available_fonts = set(tkfont.families(self.root))
        preferred_fonts = [
            "Mangal",
            "Nirmala UI",
            "Noto Sans Devanagari",
            "Noto Serif Devanagari",
            "Nirmala UI",
            "Kalimati",
            "Lohit Devanagari",
        ]
        for family in preferred_fonts:
            if family in available_fonts:
                self.font_info_text.set(f"Marathi font in use: {family}")
                return (family, 18)

        if self.local_nirmala_registered:
            self.font_info_text.set("Marathi font in use: Nirmala UI (from local font file)")
            return ("Nirmala UI", 18)

        self.font_info_text.set(
            "No Indic font detected. Install Noto Sans Devanagari on Ubuntu or use Windows with Mangal/Nirmala UI."
        )
        return ("TkDefaultFont", 16)

    def _apply_style_scale(self) -> None:
        width = max(self.root.winfo_width(), 900)
        height = max(self.root.winfo_height(), 620)
        if width < 980 or height < 690:
            hero_title = 18
            hero_body = 9
            section_label = 10
            body = 9
            muted = 8
            value = 11
            button = 9
            info_title = 8
            info_value = 11
            page_title = 13
            status = 9
        else:
            hero_title = 21
            hero_body = 10
            section_label = 11
            body = 10
            muted = 9
            value = 12
            button = 10
            info_title = 9
            info_value = 13
            page_title = 15
            status = 10

        self.style.configure("HeroTitle.TLabel", background="#1f3a5f", foreground="#ffffff", font=("Segoe UI", hero_title, "bold"))
        self.style.configure("HeroBody.TLabel", background="#1f3a5f", foreground="#d9e4f2", font=("Segoe UI", hero_body))
        self.style.configure("Section.TLabelframe.Label", background="#fffdf8", foreground="#183153", font=("Segoe UI", section_label, "bold"))
        self.style.configure("Body.TLabel", background="#fffdf8", foreground="#243447", font=("Segoe UI", body))
        self.style.configure("Muted.TLabel", background="#fffdf8", foreground="#5f6b7a", font=("Segoe UI", muted))
        self.style.configure("Value.TLabel", background="#fffdf8", foreground="#10233d", font=("Segoe UI", value, "bold"))
        self.style.configure("Primary.TButton", font=("Segoe UI", button, "bold"))
        self.style.configure("InfoTitle.TLabel", background="#eef3f8", foreground="#5a6b7b", font=("Segoe UI", info_title, "bold"))
        self.style.configure("InfoValue.TLabel", background="#eef3f8", foreground="#17324d", font=("Segoe UI", info_value, "bold"))

        if hasattr(self, "page_title_label"):
            self.page_title_label.configure(font=("Segoe UI", page_title, "bold"))
        if hasattr(self, "status_label"):
            self.status_label.configure(font=("Segoe UI", status))

    def _update_preview_box(self) -> None:
        font_to_use = self._get_display_font(self._preview_font_size())
        self.setup_preview_box.configure(state="normal", font=font_to_use)
        self.setup_preview_box.delete("1.0", "end")
        self.setup_preview_box.insert("1.0", self._format_passage_for_display(self.current_passage))
        self.setup_preview_box.configure(state="disabled")

    def _on_profile_changed(self, _event=None) -> None:
        self.current_profile = PROFILES[self.selected_profile.get()]
        self._update_language_mode()
        self._set_time_text()
        self._sync_custom_font()
        self._set_passage_for_current_selection()
        self.status_text.set("Test configuration updated.")

    def _on_practice_language_changed(self, _event=None) -> None:
        if self.current_profile.duration_minutes is None:
            self.language_var.set(self.practice_language_var.get())
            self._sync_custom_font()
            self._set_passage_for_current_selection()
            self.status_text.set("Practice language changed.")

    def _update_language_mode(self) -> None:
        if self.current_profile.duration_minutes is None:
            self.language_control.configure(state="readonly")
            self.language_var.set(self.practice_language_var.get())
        else:
            self.language_control.configure(state="disabled")
            self.language_var.set(self.current_profile.language)
        if hasattr(self, "input_box"):
            self._configure_input_widget_for_language()

    def _sync_custom_font(self) -> None:
        if hasattr(self, "passage_box"):
            self._render_passages()
        if hasattr(self, "input_box"):
            self._apply_typing_fonts()
        if hasattr(self, "result_typed_box") and self.active_result and self.pages["result"].winfo_ismapped():
            self._show_result_page()

    def _set_time_text(self) -> None:
        if self.current_profile.duration_minutes is None:
            self.timer_text.set("No Limit")
        else:
            self.timer_text.set(f"{self.current_profile.duration_minutes:02d}:00")

    def _set_passage_for_current_selection(self) -> None:
        selected_profile = PROFILES[self.selected_profile.get()]
        passage_key = selected_profile.passage_key

        if passage_key in self.external_passages and self.external_passages[passage_key]:
            picked = random.choice(self.external_passages[passage_key])
            self.current_passage = picked["text"]
            self.current_passage_label = picked["label"]
        else:
            self.current_passage = self._pick_builtin_passage(self.language_var.get())
            self.current_passage_label = "Built-in passage"

        self._render_passages()

    def _render_passages(self) -> None:
        font_to_use = self._get_display_font(self._passage_font_size())
        display_text = self._format_passage_for_display(self.current_passage)

        if hasattr(self, "passage_box"):
            self.passage_box.configure(state="normal", font=font_to_use)
            self.passage_box.delete("1.0", "end")
            self.passage_box.insert("1.0", display_text)
            self.passage_box.configure(state="disabled")

            # Add breathing room so passages are easier to read sentence by sentence.
            self.passage_box.configure(spacing1=4, spacing2=3, spacing3=6, tabs=("2c",))

        self._update_preview_box()

    def _refresh_passage(self) -> None:
        if self.test_running:
            messagebox.showinfo("Test Running", "Finish or reset the current test first.")
            return

        self._set_passage_for_current_selection()
        self.status_text.set(f"Passage ready. Source: {self.current_passage_label}")

    def start_test(self) -> None:
        if self.test_running:
            return

        self.current_profile = PROFILES[self.selected_profile.get()]
        self._update_language_mode()
        self._sync_custom_font()
        self._set_passage_for_current_selection()

        candidate_name = self.candidate_name_var.get().strip()
        if not candidate_name:
            messagebox.showwarning("Candidate Name", "Please enter candidate name.")
            return

        if not self.current_passage.strip():
            messagebox.showwarning("No Passage", "Please load a passage before starting.")
            return

        self.input_box.delete("1.0", "end")
        self._configure_input_widget_for_language()
        self._apply_typing_fonts()
        self.test_running = True
        self.start_time = time.time()
        self._set_time_text()
        self.status_text.set("Test is running.")
        self._show_page("test")
        self.input_box.focus_set()

        if self.current_profile.duration_minutes is not None:
            self._schedule_timer()

    def _apply_typing_fonts(self) -> None:
        font_to_use = self._get_display_font(self._passage_font_size())
        self.passage_box.configure(font=font_to_use)
        self.input_box.configure(font=font_to_use)
        self.result_typed_box.configure(font=font_to_use)
        self.input_box.configure(spacing1=4, spacing2=3, spacing3=6, tabs=("2c",))
        self.result_typed_box.configure(spacing1=4, spacing2=3, spacing3=6, tabs=("2c",))

    def _configure_input_widget_for_language(self) -> None:
        if not hasattr(self, "input_box"):
            return

        common_options = {
            "wrap": "word",
            "exportselection": False,
            "insertwidth": 2,
            "takefocus": True,
        }

        if sys.platform.startswith("win") and self.language_var.get() in {"Marathi", "Hindi"}:
            self.input_box.configure(
                undo=False,
                autoseparators=False,
                maxundo=0,
                **common_options,
            )
            self.status_text.set("Windows Marathi/Hindi compatibility mode enabled for typing.")
            return

        self.input_box.configure(
            undo=True,
            autoseparators=True,
            maxundo=-1,
            **common_options,
        )

    def _schedule_timer(self) -> None:
        if not self.test_running or self.current_profile.duration_minutes is None:
            return

        total_seconds = self.current_profile.duration_minutes * 60
        elapsed_seconds = int(time.time() - self.start_time)
        remaining = max(0, total_seconds - elapsed_seconds)
        minutes, seconds = divmod(remaining, 60)
        self.timer_text.set(f"{minutes:02d}:{seconds:02d}")

        if remaining == 0:
            self.finish_test(time_up=True)
            return

        self.timer_job = self.root.after(250, self._schedule_timer)

    def finish_test(self, time_up: bool = False) -> None:
        if not self.test_running:
            self.status_text.set("No running test to finish.")
            return

        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.test_running = False
        elapsed = max(time.time() - self.start_time, 1)
        self._calculate_results(elapsed)
        self._show_result_page()

        if time_up:
            self.status_text.set("Time is over. Result calculated.")
            messagebox.showinfo("Test Complete", "The timed test has ended.")
        else:
            self.status_text.set("Test finished. Result calculated.")

    def reset_test(self) -> None:
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.test_running = False
        self.input_box.delete("1.0", "end")
        self._set_time_text()
        self.status_text.set("Current test reset.")

    def _back_to_setup(self) -> None:
        if self.test_running:
            confirmed = messagebox.askyesno(
                "Leave Test",
                "The current test is running. Do you want to stop it and return to setup?",
            )
            if not confirmed:
                return
            self.reset_test()
        self._show_page("setup")
        self.status_text.set("Back on setup page.")

    def _calculate_results(self, elapsed_seconds: float) -> None:
        source_words = self._tokenize(self.current_passage)
        typed_text = self.input_box.get("1.0", "end").strip()
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
            "Candidate Name": self.candidate_name_var.get().strip(),
            "Exam Type": self.current_profile.name,
            "Language": self.language_var.get(),
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
            widget.configure(text=self.active_result.get(label, "-"))

        font_to_use = self._get_display_font(self._passage_font_size())
        self.result_typed_box.configure(state="normal", font=font_to_use)
        self.result_typed_box.delete("1.0", "end")
        self.result_typed_box.insert("1.0", self.active_result.get("Typed Text", ""))
        self.result_typed_box.configure(state="disabled")

    def _get_display_font(self, size: int | None = None) -> tuple[str, int]:
        chosen_size = size or self.english_font_size
        if self.language_var.get() in {"Marathi", "Hindi"}:
            return (self.indic_font_family, max(chosen_size, 13))
        return (self.english_font_family, max(chosen_size, 12))

    def _preview_font_size(self) -> int:
        width = max(self.root.winfo_width(), 900)
        if width < 980:
            return 13
        return 15

    def _passage_font_size(self) -> int:
        width = max(self.root.winfo_width(), 900)
        height = max(self.root.winfo_height(), 620)
        content_length = max(len(self.current_passage), 1)
        size = 16
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

    def _on_window_resized(self, event) -> None:
        if event.widget is not self.root:
            return
        if self.resize_job is not None:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(120, self._apply_responsive_layout)

    def _apply_responsive_layout(self) -> None:
        self.resize_job = None
        self._apply_style_scale()
        self._apply_header_layout()
        self._sync_custom_font()

    def _apply_header_layout(self) -> None:
        if self.top_bar is None:
            return
        width = max(self.root.winfo_width(), 900)
        compact = width < 980
        if compact:
            self.top_bar.columnconfigure((0, 1, 2), weight=0)
            self.top_bar.columnconfigure(0, weight=1)
            self.header_exam_box.grid_configure(row=0, column=0, padx=0, pady=(0, 8))
            self.header_language_box.grid_configure(row=1, column=0, padx=0, pady=(0, 8))
            self.header_timer_box.grid_configure(row=2, column=0, padx=0, pady=0)
        else:
            self.top_bar.columnconfigure((0, 1, 2), weight=1)
            self.header_exam_box.grid_configure(row=0, column=0, padx=(0, 8), pady=0)
            self.header_language_box.grid_configure(row=0, column=1, padx=4, pady=0)
            self.header_timer_box.grid_configure(row=0, column=2, padx=(8, 0), pady=0)

    def _on_input_key_release(self, _event=None) -> None:
        if self.language_var.get() not in {"Marathi", "Hindi"}:
            return
        typed_text = self.input_box.get("1.0", "end-1c")
        if typed_text and set(typed_text) == {"?"}:
            self.status_text.set(
                "Unicode input is not reaching the app. Use a Unicode Devanagari keyboard/font; legacy ISM layouts may send only '?'."
            )

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

    def _load_png(self, file_name: str) -> tk.PhotoImage | None:
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
        if not os.path.exists(image_path):
            return None
        try:
            return tk.PhotoImage(file=image_path)
        except tk.TclError:
            return None

    def _set_banner_image(
        self,
        label: tk.Label,
        image: tk.PhotoImage | None,
        fallback_text: str,
    ) -> None:
        if image is not None:
            label.configure(
                image=image,
                text="",
                borderwidth=1,
                relief="solid",
                padx=6,
                pady=6,
                bg="#fffdf8",
            )
            label.image = image
        else:
            label.configure(
                image="",
                text=fallback_text,
                font=("Segoe UI", 11, "bold"),
                fg="#183153",
                padx=20,
                pady=20,
                borderwidth=1,
                relief="solid",
                bg="#fffdf8",
            )

    def _show_phone_number(self) -> None:
        messagebox.showinfo("Institute Contact", f"{COMPANY_NAME}\nCall: {COMPANY_PHONE}")

    def _call_institute(self) -> None:
        try:
            webbrowser.open(f"tel:{COMPANY_PHONE}")
        except Exception:
            self._show_phone_number()

    def _start_new_test_from_result(self) -> None:
        self.input_box.delete("1.0", "end")
        self._show_page("setup")
        self.status_text.set("Ready for a new test.")

    def _retry_current_test(self) -> None:
        self.input_box.delete("1.0", "end")
        self._show_page("test")
        self.start_test()

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
    root = tk.Tk()
    TypingExamApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
