// ── State ────────────────────────────────────────────────────────
let currentProfileKey = "English 30 WPM";
let currentLanguage = "English";
let practiceLanguage = "English";
let currentPassage = { text: "", label: "" };
let testRunning = false;
let startTime = 0;
let timerInterval = null;

// ── DOM refs ────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

// ── Page navigation ─────────────────────────────────────────────
function showPage(name) {
    document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
    $("page-" + name).classList.add("active");

    const titles = { setup: "1. Test Setup", test: "2. Typing Test", result: "3. Result" };
    $("page-title").textContent = titles[name] || "";
}

// ── Profile / language handling ─────────────────────────────────
function populateProfileDropdown() {
    const sel = $("exam-type");
    sel.innerHTML = "";
    for (const name of Object.keys(PROFILES)) {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        sel.appendChild(opt);
    }
    sel.value = currentProfileKey;
}

function onProfileChanged() {
    currentProfileKey = $("exam-type").value;
    const profile = PROFILES[currentProfileKey];

    // Update language mode
    const langSel = $("language-select");
    if (profile.duration_minutes === null) {
        langSel.disabled = false;
        currentLanguage = practiceLanguage;
    } else {
        langSel.disabled = true;
        currentLanguage = profile.language;
        langSel.value = currentLanguage;
    }

    updateTimeDisplay();
    updateFontClass();
    loadRandomPassage();
    setStatus("Test configuration updated.");
}

function onLanguageChanged() {
    const profile = PROFILES[currentProfileKey];
    if (profile.duration_minutes === null) {
        practiceLanguage = $("language-select").value;
        currentLanguage = practiceLanguage;
        updateFontClass();
        loadRandomPassage();
        setStatus("Practice language changed.");
    }
}

function updateTimeDisplay() {
    const profile = PROFILES[currentProfileKey];
    const text = profile.duration_minutes === null
        ? "No Limit"
        : String(profile.duration_minutes).padStart(2, "0") + ":00";
    $("setup-time").textContent = text;
}

function updateFontClass() {
    const isIndic = currentLanguage === "Marathi" || currentLanguage === "Hindi";
    const elements = [
        $("passage-preview"),
        $("passage-display"),
        $("typing-area"),
        $("result-typed-text"),
    ];
    elements.forEach((el) => {
        if (!el) return;
        if (isIndic) {
            el.classList.add("font-devanagari");
        } else {
            el.classList.remove("font-devanagari");
        }
    });

    // Set lang attribute on textarea for better IME behavior
    const ta = $("typing-area");
    if (ta) {
        ta.lang = isIndic ? (currentLanguage === "Marathi" ? "mr" : "hi") : "en";
    }
}

// ── Passage management ──────────────────────────────────────────
function loadRandomPassage() {
    const profile = PROFILES[currentProfileKey];
    const passageKey = profile.passage_key;
    let pool = [];

    if (passageKey === "practice") {
        // Practice mode: use practice language, no DOCX for practice
        const builtinPractice = PASSAGES.builtin.practice || {};
        pool = builtinPractice[practiceLanguage] || [];
    } else {
        // Prefer DOCX passages, fallback to built-in
        const docxPool = (PASSAGES.docx && PASSAGES.docx[passageKey]) || [];
        const builtinPool = (PASSAGES.builtin && PASSAGES.builtin[passageKey]) || [];
        pool = docxPool.length > 0 ? docxPool : builtinPool;
    }

    if (pool.length > 0) {
        currentPassage = pool[Math.floor(Math.random() * pool.length)];
    } else {
        currentPassage = { text: "No passages available for this selection.", label: "None" };
    }

    updatePassagePreview();
}

function formatPassageForDisplay(text) {
    const lines = text.replace(/\r\n/g, "\n").split("\n");
    for (let i = 0; i < lines.length; i++) {
        if (lines[i].trim()) {
            if (!lines[i].startsWith("\t")) {
                lines[i] = "\t" + lines[i];
            }
            break;
        }
    }
    return lines.join("\n");
}

function updatePassagePreview() {
    const preview = $("passage-preview");
    if (preview) {
        preview.textContent = formatPassageForDisplay(currentPassage.text);
    }
}

// ── Status helper ───────────────────────────────────────────────
function setStatus(msg) {
    $("status-text").textContent = msg;
}

// ── Test flow ───────────────────────────────────────────────────
function startTest() {
    if (testRunning) return;

    const candidateName = $("candidate-name").value.trim();
    if (!candidateName) {
        alert("Please enter candidate name.");
        return;
    }
    if (!currentPassage.text.trim()) {
        alert("Please load a passage before starting.");
        return;
    }

    const profile = PROFILES[currentProfileKey];

    // Update test page header
    $("header-exam").textContent = currentProfileKey;
    $("header-language").textContent = currentLanguage;

    // Set passage display
    $("passage-display").textContent = formatPassageForDisplay(currentPassage.text);
    updateFontClass();

    // Clear typing area
    const ta = $("typing-area");
    ta.value = "";
    ta.disabled = false;

    // Start timer
    testRunning = true;
    startTime = Date.now();

    if (profile.duration_minutes !== null) {
        startTimer(profile.duration_minutes);
    } else {
        $("timer-display").textContent = "No Limit";
    }

    if (currentLanguage === "Marathi" || currentLanguage === "Hindi") {
        setStatus("Test is running. Enable ISM (Scroll Lock) to type in " + currentLanguage + ".");
    } else {
        setStatus("Test is running.");
    }

    showPage("test");
    ta.focus();
}

function startTimer(durationMinutes) {
    const endTime = Date.now() + durationMinutes * 60 * 1000;

    function tick() {
        const remaining = Math.max(0, endTime - Date.now());
        const mins = Math.floor(remaining / 60000);
        const secs = Math.floor((remaining % 60000) / 1000);
        $("timer-display").textContent =
            String(mins).padStart(2, "0") + ":" + String(secs).padStart(2, "0");

        if (remaining <= 0) {
            clearInterval(timerInterval);
            timerInterval = null;
            finishTest(true);
        }
    }

    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(tick, 250);
    tick();
}

async function finishTest(timeUp) {
    if (!testRunning) {
        setStatus("No running test to finish.");
        return;
    }

    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    testRunning = false;

    const elapsedSeconds = Math.max((Date.now() - startTime) / 1000, 1);
    const typedText = $("typing-area").value;

    try {
        const response = await fetch("/api/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                passage_text: currentPassage.text,
                typed_text: typedText,
                profile_name: currentProfileKey,
                elapsed_seconds: elapsedSeconds,
                candidate_name: $("candidate-name").value.trim(),
                passage_label: currentPassage.label,
                language: currentLanguage,
            }),
        });
        const result = await response.json();
        showResults(result, typedText);
    } catch (err) {
        alert("Error scoring exam: " + err.message);
        return;
    }

    if (timeUp) {
        alert("Time is over!");
        setStatus("Time is over. Result calculated.");
    } else {
        setStatus("Test finished. Result calculated.");
    }
}

function resetTest() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    testRunning = false;
    $("typing-area").value = "";

    const profile = PROFILES[currentProfileKey];
    if (profile.duration_minutes !== null) {
        $("timer-display").textContent =
            String(profile.duration_minutes).padStart(2, "0") + ":00";
    }
    setStatus("Current test reset.");
}

function backToSetup() {
    if (testRunning) {
        if (!confirm("The current test is running. Do you want to stop it and return to setup?")) {
            return;
        }
        resetTest();
    }
    showPage("setup");
    setStatus("Back on setup page.");
}

// ── Results ─────────────────────────────────────────────────────
function showResults(result, typedText) {
    const mapping = {
        "Candidate Name": "res-candidate",
        "Exam Type": "res-exam",
        "Language": "res-language",
        "Passage Source": "res-source",
        "Elapsed Time": "res-time",
        "Total Typed Words": "res-total",
        "Matched Words": "res-matched",
        "Mistakes": "res-mistakes",
        "Accuracy": "res-accuracy",
        "Speed (WPM)": "res-speed",
        "Marks": "res-marks",
        "Target": "res-target",
        "Result": "res-result",
    };

    for (const [key, id] of Object.entries(mapping)) {
        const el = $(id);
        if (el) el.textContent = result[key] || "-";
    }

    // Show typed text
    const reviewEl = $("result-typed-text");
    if (reviewEl) {
        reviewEl.textContent = typedText;
    }

    updateFontClass();
    showPage("result");
}

function startNewTest() {
    showPage("setup");
    setStatus("Ready for a new test.");
}

function retrySameTest() {
    showPage("test");
    startTest();
}

// ── ISM detection ───────────────────────────────────────────────
function onTypingInput() {
    if (currentLanguage !== "Marathi" && currentLanguage !== "Hindi") return;
    const text = $("typing-area").value.replace(/[\s\n]/g, "");
    if (text && [...new Set(text)].every((c) => c === "?")) {
        setStatus(
            "ISM is sending '?' -- switch ISM to Unicode mode, or use Windows " +
            "Marathi/Hindi keyboard (Settings > Language) instead of legacy ISM."
        );
    }
}

// ── Initialization ──────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    populateProfileDropdown();

    $("exam-type").addEventListener("change", onProfileChanged);
    $("language-select").addEventListener("change", onLanguageChanged);
    $("typing-area").addEventListener("input", onTypingInput);

    // Initial state
    onProfileChanged();
    showPage("setup");
});
