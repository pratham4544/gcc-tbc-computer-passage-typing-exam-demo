from __future__ import annotations

import json
import os
import random
import sys
import threading
import webbrowser
import zipfile
from dataclasses import dataclass
from xml.etree import ElementTree as ET

from flask import Flask, jsonify, render_template, request


def _get_base_dir() -> str:
    """Return the base directory — works both when running as script and as PyInstaller .exe."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

# ── passages ────────────────────────────────────────────────────────

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


# ── exam profiles ───────────────────────────────────────────────────

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

COMPANY_NAME = "Pushpanjali Computer Typing Institute, Dahiwadi"
COMPANY_TAGLINE = "Free typing practice software by Pushpanjali Computer Typing Institute."
COMPANY_PHONE = "9970939341"
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


# ── DOCX passage loading ───────────────────────────────────────────

def extract_docx_text(file_path: str) -> str:
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


def match_passage_key(normalized_path: str) -> str | None:
    for passage_key, markers in QUESTION_PAPER_KEYS.items():
        if all(marker in normalized_path for marker in markers):
            return passage_key
    return None


def load_external_docx_passages() -> dict[str, list[dict[str, str]]]:
    root_dir = os.path.join(_get_base_dir(), QUESTION_PAPER_DIR)
    loaded: dict[str, list[dict[str, str]]] = {key: [] for key in QUESTION_PAPER_KEYS}
    if not os.path.isdir(root_dir):
        return loaded
    for dirpath, _, filenames in os.walk(root_dir):
        normalized_path = dirpath.lower().replace("_", " ")
        for filename in filenames:
            if not filename.lower().endswith(".docx"):
                continue
            passage_key = match_passage_key(normalized_path)
            if passage_key is None:
                continue
            file_path = os.path.join(dirpath, filename)
            text = extract_docx_text(file_path)
            if not text:
                continue
            loaded[passage_key].append({"label": filename, "text": text})
    return loaded


EXTERNAL_PASSAGES = load_external_docx_passages()


# ── scoring helpers ─────────────────────────────────────────────────

def tokenize(text: str) -> list[str]:
    cleaned = text.replace("\n", " ").split()
    return [word.strip(".,!?;:\"'()[]{}") for word in cleaned if word.strip()]


def calculate_marks(matched_words: int, profile: ExamProfile) -> int:
    if profile.duration_minutes is None or profile.target_wpm == 0:
        return 0
    target_words = profile.target_wpm * profile.duration_minutes
    if target_words <= 0:
        return 0
    marks = round((matched_words / target_words) * TOTAL_MARKS)
    return max(0, min(TOTAL_MARKS, marks))


def calculate_result(marks: int, mistakes: int, profile: ExamProfile) -> str:
    if profile.duration_minutes is None:
        return "Practice"
    if marks >= PASS_MARKS and mistakes <= MAX_ALLOWED_MISTAKES:
        return "Pass"
    return "Fail"


def format_elapsed(elapsed_seconds: float) -> str:
    total_seconds = int(elapsed_seconds)
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


# ── build passages dict for frontend ───────────────────────────────

def build_passages_dict() -> dict:
    builtin = {
        "eng30": [{"label": "Built-in passage", "text": p} for p in ENGLISH_PASSAGES],
        "eng40": [{"label": "Built-in passage", "text": p} for p in ENGLISH_PASSAGES],
        "mar30": [{"label": "Built-in passage", "text": p} for p in MARATHI_PASSAGES],
        "mar40": [{"label": "Built-in passage", "text": p} for p in MARATHI_PASSAGES],
        "hin30": [{"label": "Built-in passage", "text": p} for p in HINDI_PASSAGES],
        "hin40": [{"label": "Built-in passage", "text": p} for p in HINDI_PASSAGES],
        "practice": {
            "English": [{"label": "Built-in passage", "text": p} for p in ENGLISH_PASSAGES],
            "Marathi": [{"label": "Built-in passage", "text": p} for p in MARATHI_PASSAGES],
            "Hindi": [{"label": "Built-in passage", "text": p} for p in HINDI_PASSAGES],
        },
    }
    return {"docx": EXTERNAL_PASSAGES, "builtin": builtin}


def build_profiles_dict() -> dict:
    return {
        name: {
            "name": p.name,
            "language": p.language,
            "duration_minutes": p.duration_minutes,
            "target_wpm": p.target_wpm,
            "passage_key": p.passage_key,
        }
        for name, p in PROFILES.items()
    }


# ── Flask app ───────────────────────────────────────────────────────

BASE_DIR = _get_base_dir()
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


@app.route("/")
def index():
    return render_template(
        "index.html",
        profiles_json=json.dumps(build_profiles_dict(), ensure_ascii=False),
        passages_json=json.dumps(build_passages_dict(), ensure_ascii=False),
        company_name=COMPANY_NAME,
        company_tagline=COMPANY_TAGLINE,
        company_phone=COMPANY_PHONE,
        total_marks=TOTAL_MARKS,
        pass_marks=PASS_MARKS,
        max_mistakes=MAX_ALLOWED_MISTAKES,
    )


@app.route("/api/score", methods=["POST"])
def score_exam():
    data = request.get_json()
    passage_text = data["passage_text"]
    typed_text = data["typed_text"]
    profile_name = data["profile_name"]
    elapsed_seconds = float(data["elapsed_seconds"])
    candidate_name = data["candidate_name"]
    passage_label = data.get("passage_label", "Unknown")
    language = data.get("language", "English")

    profile = PROFILES.get(profile_name)
    if profile is None:
        return jsonify({"error": "Unknown profile"}), 400

    source_words = tokenize(passage_text)
    typed_words = tokenize(typed_text)

    matched_words = sum(
        1 for expected, actual in zip(source_words, typed_words) if expected == actual
    )
    total_typed = len(typed_words)
    mistakes = max(total_typed - matched_words, 0)
    accuracy = (matched_words / total_typed * 100) if total_typed else 0.0
    elapsed_minutes = elapsed_seconds / 60
    speed_wpm = (matched_words / elapsed_minutes) if elapsed_minutes else 0.0
    marks = calculate_marks(matched_words, profile)
    result_text = calculate_result(marks, mistakes, profile)

    display_language = profile.language if profile.duration_minutes else language
    target = f"{profile.target_wpm} WPM" if profile.target_wpm else "Practice"

    return jsonify({
        "Candidate Name": candidate_name,
        "Exam Type": profile.name,
        "Language": display_language,
        "Passage Source": passage_label,
        "Elapsed Time": format_elapsed(elapsed_seconds),
        "Total Typed Words": str(total_typed),
        "Matched Words": str(matched_words),
        "Mistakes": str(mistakes),
        "Accuracy": f"{accuracy:.2f}%",
        "Speed (WPM)": f"{speed_wpm:.2f}",
        "Marks": f"{marks}/{TOTAL_MARKS}",
        "Target": target,
        "Result": result_text,
    })


if __name__ == "__main__":
    url = "http://127.0.0.1:5000"
    print(f"Starting Typing Exam Practice at {url}")
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
