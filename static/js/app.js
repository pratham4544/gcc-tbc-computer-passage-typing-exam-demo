const { useState, useEffect, useRef, useCallback } = React;

// ── Helpers ─────────────────────────────────────────────────────
function formatPassage(text) {
    const lines = text.replace(/\r\n/g, "\n").split("\n");
    for (let i = 0; i < lines.length; i++) {
        if (lines[i].trim()) {
            if (!lines[i].startsWith("\t")) lines[i] = "\t" + lines[i];
            break;
        }
    }
    return lines.join("\n");
}

function pickRandom(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function getPassagePool(passageKey, language) {
    if (passageKey === "practice") {
        return (PASSAGES.builtin.practice || {})[language] || [];
    }
    const docx = (PASSAGES.docx && PASSAGES.docx[passageKey]) || [];
    const builtin = (PASSAGES.builtin && PASSAGES.builtin[passageKey]) || [];
    return docx.length > 0 ? docx : builtin;
}

function isIndic(lang) {
    return lang === "Marathi" || lang === "Hindi";
}

function fontClass(lang) {
    return isIndic(lang) ? "font-devanagari" : "";
}

function langAttr(lang) {
    if (lang === "Marathi") return "mr";
    if (lang === "Hindi") return "hi";
    return "en";
}

// ── Hero ────────────────────────────────────────────────────────
function Hero() {
    return (
        <div id="hero">
            <h1>Offline Typing Exam Practice</h1>
            <p>Browser-based exam simulator with English, Marathi, Hindi, and optional exam-question DOCX loading.</p>
        </div>
    );
}

// ── NavBar ──────────────────────────────────────────────────────
function NavBar({ title, status }) {
    return (
        <div id="nav-bar">
            <span id="page-title">{title}</span>
            <span id="status-text">{status}</span>
        </div>
    );
}

// ── SetupPage ───────────────────────────────────────────────────
function SetupPage({ onStart, candidateName, setCandidateName, profileKey, setProfileKey, language, setLanguage, passage, onLoadPassage }) {
    const profile = PROFILES[profileKey];
    const isPractice = profile.duration_minutes === null;
    const timeText = isPractice ? "No Limit" : String(profile.duration_minutes).padStart(2, "0") + ":00";

    return (
        <div className="setup-card">
            <div className="section-group">
                <h3>Exam Setup</h3>
                <p className="body-text" style={{ textAlign: "center" }}>Select exam details and start the practice test.</p>
                <div className="form-grid">
                    <label className="body-text">Candidate Name</label>
                    <input type="text" value={candidateName} onChange={e => setCandidateName(e.target.value)} placeholder="Enter your name" />

                    <label className="body-text">Exam Type</label>
                    <select value={profileKey} onChange={e => setProfileKey(e.target.value)}>
                        {Object.keys(PROFILES).map(k => <option key={k} value={k}>{k}</option>)}
                    </select>

                    <label className="body-text">Language</label>
                    <select value={language} onChange={e => setLanguage(e.target.value)} disabled={!isPractice}>
                        <option value="English">English</option>
                        <option value="Marathi">Marathi</option>
                        <option value="Hindi">Hindi</option>
                    </select>

                    <label className="body-text">Time</label>
                    <span className="value-label">{timeText}</span>
                </div>
            </div>

            <div className="section-group">
                <h3>Current Passage Preview</h3>
                <div className={"passage-display " + fontClass(language)}>
                    {formatPassage(passage.text)}
                </div>
            </div>

            <p className="muted-text" style={{ textAlign: "center" }}>
                Marathi and Hindi need a Devanagari font. This app uses Nirmala UI, Mangal, or Noto Sans Devanagari.
            </p>

            <div className="actions-center">
                <button onClick={onLoadPassage}>Load Random Passage</button>
                <button className="btn-primary" onClick={onStart}>Start Test</button>
            </div>

            <div className="institute-info">
                <h3 className="institute-name">{CONFIG.companyName}</h3>
                <p className="body-text">Call: {CONFIG.companyPhone}</p>
                <img src={CONFIG.img1} alt="Institute Banner" className="banner-img" />
            </div>
        </div>
    );
}

// ── TestPage ────────────────────────────────────────────────────
function TestPage({ profileKey, language, passage, timerText, typedText, setTypedText, onFinish, onReset, onBack }) {
    const taRef = useRef(null);

    useEffect(() => {
        if (taRef.current) taRef.current.focus();
    }, []);

    const handleInput = useCallback((e) => {
        setTypedText(e.target.value);
    }, [setTypedText]);

    return (
        <div className="test-card">
            <div className="info-bar">
                <div className="info-card">
                    <span className="info-title">Exam Type</span>
                    <span className="info-value">{profileKey}</span>
                </div>
                <div className="info-card">
                    <span className="info-title">Language</span>
                    <span className="info-value">{language}</span>
                </div>
                <div className="info-card">
                    <span className="info-title">Time Left</span>
                    <span className="info-value info-mono">{timerText}</span>
                </div>
            </div>

            <div className="test-split">
                <div className="section-group test-panel">
                    <h3>Passage</h3>
                    <div className={"passage-display " + fontClass(language)}>
                        {formatPassage(passage.text)}
                    </div>
                </div>
                <div className="section-group test-panel">
                    <h3>Typing Area</h3>
                    <textarea
                        ref={taRef}
                        className={fontClass(language)}
                        lang={langAttr(language)}
                        spellCheck={false}
                        autoComplete="off"
                        placeholder="Start typing here..."
                        value={typedText}
                        onChange={handleInput}
                    />
                </div>
            </div>

            <div className="test-actions">
                <button onClick={onBack}>Back to Setup</button>
                <div className="actions-right">
                    <button onClick={onReset}>Reset Test</button>
                    <button className="btn-primary" onClick={() => onFinish(false)}>Finish Test</button>
                </div>
            </div>
        </div>
    );
}

// ── ResultPage ──────────────────────────────────────────────────
function ResultPage({ result, typedText, language, onNewTest, onRetry }) {
    const metrics = [
        ["Candidate Name", result["Candidate Name"]],
        ["Exam Type", result["Exam Type"]],
        ["Language", result["Language"]],
        ["Passage Source", result["Passage Source"]],
        ["Elapsed Time", result["Elapsed Time"]],
        ["Total Typed Words", result["Total Typed Words"]],
        ["Matched Words", result["Matched Words"]],
        ["Mistakes", result["Mistakes"]],
        ["Accuracy", result["Accuracy"]],
        ["Speed (WPM)", result["Speed (WPM)"]],
        ["Marks", result["Marks"]],
        ["Target", result["Target"]],
        ["Result", result["Result"]],
    ];

    const resultValue = result["Result"] || "";
    const resultClass = resultValue === "Pass" ? "result-pass" : resultValue === "Fail" ? "result-fail" : "";

    return (
        <div className="result-card">
            <h2 className="result-title">Result Summary</h2>
            <div className="result-content">
                <div className="metrics-grid">
                    {metrics.map(([label, val]) => (
                        <div className="metric-row" key={label}>
                            <span className="body-text">{label}</span>
                            <span className={`value-label ${label === "Result" ? resultClass : ""}`}>{val || "-"}</span>
                        </div>
                    ))}
                </div>
                <div className="section-group">
                    <h3>Typed Text Review</h3>
                    <div className={"passage-display " + fontClass(language)}>{typedText}</div>
                </div>
            </div>

            <div className="actions-center">
                <button className="btn-primary" onClick={onNewTest}>New Test</button>
                <button onClick={onRetry}>Retry Same Test</button>
            </div>

            <div className="section-group institute-section">
                <img src={CONFIG.img2} alt="Result Banner" className="banner-img" />
                <h3 className="institute-name">{CONFIG.companyName}</h3>
                <p className="body-text">{CONFIG.companyTagline}</p>
                <p className="body-text">Call: {CONFIG.companyPhone}</p>
                <div className="actions-center">
                    <button className="btn-primary" onClick={() => window.open("tel:" + CONFIG.companyPhone)}>Call Institute</button>
                    <button onClick={() => alert(CONFIG.companyName + "\nCall: " + CONFIG.companyPhone)}>Show Number</button>
                </div>
            </div>
        </div>
    );
}

// ── App (main) ──────────────────────────────────────────────────
function App() {
    const [page, setPage] = useState("setup");
    const [status, setStatus] = useState("Choose a test type and load a passage.");
    const [candidateName, setCandidateName] = useState("");
    const [profileKey, setProfileKey] = useState("English 30 WPM");
    const [practiceLanguage, setPracticeLanguage] = useState("English");
    const [passage, setPassage] = useState({ text: "", label: "" });
    const [typedText, setTypedText] = useState("");
    const [timerText, setTimerText] = useState("07:00");
    const [result, setResult] = useState({});
    const [resultTypedText, setResultTypedText] = useState("");

    const testRunningRef = useRef(false);
    const startTimeRef = useRef(0);
    const timerRef = useRef(null);
    const passageRef = useRef(passage);

    // Current profile & language derived
    const profile = PROFILES[profileKey];
    const isPractice = profile.duration_minutes === null;
    const language = isPractice ? practiceLanguage : profile.language;

    // Keep passageRef in sync
    useEffect(() => { passageRef.current = passage; }, [passage]);

    // Load passage when profile or language changes
    useEffect(() => {
        loadPassage();
    }, [profileKey, practiceLanguage]);

    // Handle profile change side effects
    useEffect(() => {
        if (isPractice) {
            setTimerText("No Limit");
        } else {
            setTimerText(String(profile.duration_minutes).padStart(2, "0") + ":00");
        }
    }, [profileKey]);

    // ISM detection
    useEffect(() => {
        if (!isIndic(language)) return;
        const clean = typedText.replace(/[\s\n]/g, "");
        if (clean && [...new Set(clean)].every(c => c === "?")) {
            setStatus("ISM is sending '?' -- switch ISM to Unicode mode, or use Windows Marathi/Hindi keyboard instead of legacy ISM.");
        }
    }, [typedText, language]);

    function loadPassage() {
        const pool = getPassagePool(profile.passage_key, isPractice ? practiceLanguage : language);
        if (pool.length > 0) {
            setPassage(pickRandom(pool));
        } else {
            setPassage({ text: "No passages available for this selection.", label: "None" });
        }
    }

    function handleProfileChange(newKey) {
        setProfileKey(newKey);
        setStatus("Test configuration updated.");
    }

    function handleLanguageChange(newLang) {
        setPracticeLanguage(newLang);
        setStatus("Practice language changed.");
    }

    function handleStart() {
        if (testRunningRef.current) return;
        if (!candidateName.trim()) { alert("Please enter candidate name."); return; }
        if (!passageRef.current.text.trim()) { alert("Please load a passage before starting."); return; }

        setTypedText("");
        testRunningRef.current = true;
        startTimeRef.current = Date.now();

        if (profile.duration_minutes !== null) {
            const endTime = Date.now() + profile.duration_minutes * 60 * 1000;
            timerRef.current = setInterval(() => {
                const remaining = Math.max(0, endTime - Date.now());
                const mins = Math.floor(remaining / 60000);
                const secs = Math.floor((remaining % 60000) / 1000);
                setTimerText(String(mins).padStart(2, "0") + ":" + String(secs).padStart(2, "0"));
                if (remaining <= 0) {
                    clearInterval(timerRef.current);
                    timerRef.current = null;
                    handleFinish(true);
                }
            }, 250);
        } else {
            setTimerText("No Limit");
        }

        if (isIndic(language)) {
            setStatus("Test is running. Enable ISM (Scroll Lock) to type in " + language + ".");
        } else {
            setStatus("Test is running.");
        }
        setPage("test");
    }

    async function handleFinish(timeUp) {
        if (!testRunningRef.current) {
            setStatus("No running test to finish.");
            return;
        }
        if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
        testRunningRef.current = false;

        const elapsed = Math.max((Date.now() - startTimeRef.current) / 1000, 1);

        // Get typed text from DOM directly to avoid stale closure
        const ta = document.querySelector("#typing-area-input");
        const finalTyped = ta ? ta.value : typedText;

        try {
            const resp = await fetch("/api/score", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    passage_text: passageRef.current.text,
                    typed_text: finalTyped,
                    profile_name: profileKey,
                    elapsed_seconds: elapsed,
                    candidate_name: candidateName.trim(),
                    passage_label: passageRef.current.label,
                    language: language,
                }),
            });
            const data = await resp.json();
            setResult(data);
            setResultTypedText(finalTyped);
            setPage("result");
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

    function handleReset() {
        if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
        testRunningRef.current = false;
        setTypedText("");
        if (profile.duration_minutes !== null) {
            setTimerText(String(profile.duration_minutes).padStart(2, "0") + ":00");
        }
        setStatus("Current test reset.");
    }

    function handleBack() {
        if (testRunningRef.current) {
            if (!confirm("The current test is running. Stop and return to setup?")) return;
            handleReset();
        }
        setPage("setup");
        setStatus("Back on setup page.");
    }

    function handleNewTest() {
        setPage("setup");
        setStatus("Ready for a new test.");
    }

    function handleRetry() {
        handleStart();
    }

    const titles = { setup: "1. Test Setup", test: "2. Typing Test", result: "3. Result" };

    return (
        <>
            <Hero />
            <NavBar title={titles[page]} status={status} />

            {page === "setup" && (
                <SetupPage
                    candidateName={candidateName}
                    setCandidateName={setCandidateName}
                    profileKey={profileKey}
                    setProfileKey={handleProfileChange}
                    language={language}
                    setLanguage={handleLanguageChange}
                    passage={passage}
                    onLoadPassage={loadPassage}
                    onStart={handleStart}
                />
            )}

            {page === "test" && (
                <TestPageControlled
                    profileKey={profileKey}
                    language={language}
                    passage={passage}
                    timerText={timerText}
                    onFinish={handleFinish}
                    onReset={handleReset}
                    onBack={handleBack}
                />
            )}

            {page === "result" && (
                <ResultPage
                    result={result}
                    typedText={resultTypedText}
                    language={language}
                    onNewTest={handleNewTest}
                    onRetry={handleRetry}
                />
            )}
        </>
    );
}

// Uncontrolled textarea for test page — avoids React re-render lag while typing
function TestPageControlled({ profileKey, language, passage, timerText, onFinish, onReset, onBack }) {
    const taRef = useRef(null);

    useEffect(() => {
        if (taRef.current) taRef.current.focus();
    }, []);

    return (
        <div className="test-card">
            <div className="info-bar">
                <div className="info-card">
                    <span className="info-title">Exam Type</span>
                    <span className="info-value">{profileKey}</span>
                </div>
                <div className="info-card">
                    <span className="info-title">Language</span>
                    <span className="info-value">{language}</span>
                </div>
                <div className="info-card">
                    <span className="info-title">Time Left</span>
                    <span className="info-value info-mono">{timerText}</span>
                </div>
            </div>

            <div className="test-split">
                <div className="section-group test-panel">
                    <h3>Passage</h3>
                    <div className={"passage-display " + fontClass(language)}>
                        {formatPassage(passage.text)}
                    </div>
                </div>
                <div className="section-group test-panel">
                    <h3>Typing Area</h3>
                    <textarea
                        ref={taRef}
                        id="typing-area-input"
                        className={fontClass(language)}
                        lang={langAttr(language)}
                        spellCheck={false}
                        autoComplete="off"
                        placeholder="Start typing here..."
                        defaultValue=""
                    />
                </div>
            </div>

            <div className="test-actions">
                <button onClick={onBack}>Back to Setup</button>
                <div className="actions-right">
                    <button onClick={onReset}>Reset Test</button>
                    <button className="btn-primary" onClick={() => onFinish(false)}>Finish Test</button>
                </div>
            </div>
        </div>
    );
}

// ── Mount ───────────────────────────────────────────────────────
ReactDOM.createRoot(document.getElementById("root")).render(<App />);
