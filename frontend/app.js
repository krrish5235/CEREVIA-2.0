// ═══════════════════════════════════════════════════════════════
// CEREVIA — Frontend Application Logic
// Handles auth, API calls, dashboard, mood, journal, chatbot,
// theme management, and Java analytics integration.
// ═══════════════════════════════════════════════════════════════

// GLOBAL ROUTE PROTECTION
// Immediately checks if user is logged in.
// If not logged in and page is protected, redirects to login page.
(function protectPages() {
    const isLoggedIn = localStorage.getItem("loggedIn") === "true";
    const currentPage = window.location.pathname.toLowerCase();
    // Pages that DO NOT need login
    const publicPages = ["index.html"];
    const isPublic = publicPages.some(p => currentPage.includes(p));
    if (!isLoggedIn && !isPublic) {
        alert("⚠ Please login first!");
        window.location.href = "index.html";
    }
})();

// ─── API Configuration ─────────────────────────────────────────
const API_URL = "http://127.0.0.1:5000";           // C++ Core Backend
const CHATBOT_URL = "http://127.0.0.1:5001";       // Python AI Chatbot
const ANALYTICS_URL = "http://127.0.0.1:8080";     // Java Analytics Service

// ─── Utility Functions ─────────────────────────────────────────

async function fetchJSON(path, options = {}) {
    const res = await fetch(`${API_URL}${path}`, options);
    if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
    }
    return res.json();
}

async function fetchAnalytics(path) {
    try {
        const res = await fetch(`${ANALYTICS_URL}${path}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    } catch (err) {
        console.warn(`Analytics service unavailable: ${err.message}`);
        return null;
    }
}

// Displays popup toast message on screen
// Used across entire app for feedback messages
function showPopup(msg) {
    const popup = document.getElementById("popup");
    if (!popup) return;
    popup.innerText = msg;
    popup.classList.add("show");
    setTimeout(() => popup.classList.remove("show"), 2000);
}

// ─── Theme Management (Single Source of Truth) ──────────────────

function applyTheme(theme) {
    if (theme === "dark") {
        document.body.classList.add("dark");
    } else {
        document.body.classList.remove("dark");
    }
    syncThemeControls();
}

function setTheme(theme) {
    const normalizedTheme = theme === "dark" ? "dark" : "light";
    localStorage.setItem("theme", normalizedTheme);
    applyTheme(normalizedTheme);
}

function restoreTheme() {
    applyTheme(localStorage.getItem("theme") === "dark" ? "dark" : "light");
}

function toggleThemeFromSettings() {
    const nextTheme = document.body.classList.contains("dark") ? "light" : "dark";
    setTheme(nextTheme);
    showPopup(nextTheme === "dark" ? "Dark Mode Enabled 🌙" : "Light Mode Enabled ☀️");
}

function syncThemeControls() {
    const isDark = document.body.classList.contains("dark");
    document.querySelectorAll("#darkSwitch").forEach(control => {
        control.checked = isDark;
    });
}

window.addEventListener("storage", event => {
    if (event.key === "theme") {
        applyTheme(event.newValue === "dark" ? "dark" : "light");
    }
});

// ─── Auth Functions ─────────────────────────────────────────────

// Sets loggedIn status in localStorage
function setLoggedIn(v) {
    localStorage.setItem("loggedIn", v ? "true" : "false");
}

// Checks if user is logged in
function isLoggedIn() {
    return localStorage.getItem("loggedIn") === "true";
}

// Ensures authentication before accessing protected pages
function requireAuth() {
    const loggedIn = localStorage.getItem("loggedIn");
    console.log("AUTH CHECK:", loggedIn);
    if (loggedIn !== "true") {
        showPopup("Please login first");
        setTimeout(() => {
            window.location.href = "index.html";
        }, 500);
    }
}

// Logs user out and redirects to login
function logout() {
    localStorage.removeItem("loggedIn");
    window.location.href = "index.html";
}

// Shows forgot password box and loads security question
function showForgot() {
    const box = document.getElementById("forgotBox");
    if (box) box.style.display = "block";
    fetch(`${API_URL}/auth/question`)
        .then(r => r.json())
        .then(d => {
            const q = document.getElementById("secQuestion");
            if (q) q.innerText = d.question;
        })
        .catch(() => showPopup("Unable to load security question."));
}

// Verifies security answer with backend
// If correct → allows PIN reset
function verifyAnswer() {
    const answerEl = document.getElementById("secAnswer");
    if (!answerEl) return;
    const answer = answerEl.value;
    fetch(`${API_URL}/auth/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer })
    })
        .then(r => r.json())
        .then(d => {
            if (d.verified) {
                const box = document.getElementById("resetBox");
                if (box) box.style.display = "block";
                showPopup("Verified ✅");
            } else {
                showPopup("Wrong Answer ❌");
            }
        })
        .catch(() => showPopup("Verification failed."));
}

// Resets PIN using backend API
function resetPin() {
    const newPinEl = document.getElementById("newPinReset");
    if (!newPinEl) return;
    const newPin = newPinEl.value;
    if (!newPin) {
        showPopup("Enter a new PIN.");
        return;
    }
    fetch(`${API_URL}/auth/reset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ newPin })
    })
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                showPopup("PIN Reset Successfully ✅");
                setTimeout(() => location.reload(), 1200);
            } else {
                showPopup("Reset Failed ❌");
            }
        })
        .catch(() => showPopup("Reset failed ❌"));
}

// Handles login process
function login() {
    console.log("LOGIN START");
    const pinEl = document.getElementById("pin");
    if (!pinEl) return;
    const pin = pinEl.value;
    console.log("PIN:", pin);
    if (!pin) {
        showPopup("Enter your PIN");
        return;
    }
    fetch(`${API_URL}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ pin })
    })
        .then(res => res.json())
        .then(json => {
            if (json.success) {
                localStorage.setItem("loggedIn", "true");
                window.location.href = "dashboard.html";
            } else {
                alert("INVALID PIN ❌");
            }
        })
        .catch(err => {
            console.error(err);
            alert("BACKEND NOT REACHABLE ❌");
        });
}

// Registers or updates PIN using backend
function registerPin() {
    const pinEl = document.getElementById("newPin");
    if (!pinEl) return;
    const pin = pinEl.value;
    if (!pin) return showPopup("Enter new PIN");
    fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pin })
    })
        .then(r => r.json())
        .then(d => {
            if (d.success) showPopup("PIN updated successfully!");
            else showPopup("Error updating PIN");
        })
        .catch(() => showPopup("Backend error"));
}

// ─── Mood Functions ─────────────────────────────────────────────

// Resets mood history from backend database
function resetMood() {
    if (!confirm("Delete all mood history?")) return;
    fetch(`${API_URL}/mood/reset`, { method: "POST" })
        .then(r => r.json())
        .then(d => {
            showPopup("Mood history cleared ✅");
            loadMoods();
        });
}

// Adds new mood entry
function addMood() {
    const moodBtn = document.querySelector(".mood-btn.selected");
    const level = document.getElementById("level").value;
    const note = document.getElementById("moodNote").value;

    if (!moodBtn) {
        showPopup("⚠ Please select mood");
        return;
    }

    const moodData = {
        mood: moodBtn.dataset.mood,
        level: Number(level),
        note: note
    };

    fetch(`${API_URL}/mood/add`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(moodData)
    })
    .then(res => res.json())
    .then(data => {
        showPopup("Mood saved ✅");
        cachedSuggestion = null;
        loadMoods().then(updateDashboard);
    })
    .catch(() => showPopup("Backend error"));
}

function renderMoods() {
    loadMoods();
}

function loadMoods() {
    return fetchJSON("/mood/all")
        .then(rows => {
            const list = document.getElementById("moodList");
            if (!list) return;

            list.innerHTML = "";
            if (!rows.length) {
                list.innerHTML = "<p>No moods yet.</p>";
                return;
            }

            rows.forEach(r => {
                const div = document.createElement("div");
                div.className = "mood-entry";
                div.dataset.mood = r.mood;
                div.innerHTML = `
                    <div><strong>${r.date}</strong></div>
                    <div>Mood: ${r.mood}</div>
                    <div>Level: ${r.level}</div>
                `;
                list.appendChild(div);
            });
        })
        .catch(() => showPopup("Error loading moods"));
}

function getAllMoods() {
    return fetchJSON("/mood/all")
        .then(rows => rows || [])
        .catch(() => []);
}

// ─── Journal Functions ──────────────────────────────────────────

// Resets journal history from backend database
function resetJournal() {
    if (!confirm("Delete all journal entries?")) return;
    fetch(`${API_URL}/journal/reset`, { method: "POST" })
        .then(r => r.json())
        .then(d => {
            showPopup("Journal cleared ✅");
            loadJournal();
        });
}

function saveJournal() {
    const entryEl = document.getElementById("entry");
    const text = entryEl.value.trim();

    if (!text) {
        showPopup("Write something!");
        return;
    }

    fetch(`${API_URL}/journal/add`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text })
    })
    .then(res => res.json())
    .then(data => {
        showPopup("Journal saved ✅");
        loadJournal();
        updateDashboard();
    })
    .catch(() => showPopup("Backend error"));

    entryEl.value = "";
}

function loadJournal() {
    return fetchJSON("/journal/all")
        .then(rows => {
            const list = document.getElementById("journalList");
            if (!list) return;

            list.innerHTML = "";

            rows.forEach(entry => {
                const div = document.createElement("div");
                div.className = "journal-entry";

                div.innerHTML = `
                    <div>${entry.date}</div>
                    <div>${entry.text}</div>
                `;

                list.appendChild(div);
            });
        })
        .catch(() => showPopup("Error loading journal"));
}

function deleteJournal(index) {
    showPopup("Delete is not supported from backend history view.");
}

// ─── Dashboard Functions ────────────────────────────────────────

// Checks crisis status from backend
// Shows emergency box if crisis detected
function checkCrisisStatus() {
    return fetch(`${API_URL}/stats/crisis`)
        .then(r => r.json())
        .then(d => {
            const box = document.getElementById("emergencyBox");
            const el = document.getElementById("suggestionText");
            const emergencyText = box ? box.querySelector(".emergency-text") : null;

            if (d.crisis) {
                if (box) box.style.display = "block";
                if (el && d.message) {
                    el.textContent = d.message;
                }
                if (emergencyText && d.contact) {
                    emergencyText.textContent = `Crisis detected after 3 consecutive Sad/Angry moods. Please contact a doctor now at ${d.contact}.`;
                }
            } else {
                if (box) box.style.display = "none";
            }
        });
}

// Fetches emergency contact number from backend
function callEmergency() {
    fetch(`${API_URL}/emergency/contact`)
        .then(r => r.json())
        .then(d => {
            const number = d.contact;
            if (number) {
                window.location.href = `tel:${number}`;
            } else {
                showPopup("No emergency contact configured.");
            }
        })
        .catch(() => {
            showPopup("Unable to fetch emergency contact.");
        });
}

let cachedSuggestion = null;

function updateSuggestion() {
    const suggestionEl = document.getElementById("suggestionText");
    if (!suggestionEl) return Promise.resolve();

    if (cachedSuggestion) {
        suggestionEl.textContent = cachedSuggestion;
        return Promise.resolve();
    }

    return fetchJSON("/suggestion/today")
        .then(d => {
            cachedSuggestion = d.message || "Take care of yourself today.";
            suggestionEl.textContent = cachedSuggestion;
        })
        .catch(() => {
            suggestionEl.textContent = "Unable to load suggestion.";
        });
}

function updateJournalCount() {
    const el = document.getElementById("journalCount");
    if (!el) return Promise.resolve();
    return fetchJSON("/journal/count")
        .then(d => {
            el.textContent = Number.isFinite(d.count) ? d.count : 0;
        })
        .catch(() => {
            el.textContent = "0";
        });
}

function updateLatestMood() {
    const el = document.getElementById("latestMoodText");
    if (!el) return Promise.resolve();
    return fetchJSON("/stats/latestMood")
        .then(d => {
            el.textContent = d.mood || "--";
        })
        .catch(() => {
            el.textContent = "--";
        });
}

function updateMostFrequentMood() {
    const el = document.getElementById("mostFrequentMood");
    if (!el) return Promise.resolve();
    return fetchJSON("/stats/frequentMood")
        .then(d => {
            el.textContent = d.mood || "--";
        })
        .catch(() => {
            el.textContent = "--";
        });
}

function updateMoodScore() {
    const percentEl = document.getElementById("moodPercent");
    const big = document.getElementById("avgMoodBig");
    const ring = document.querySelector(".progress-ring circle.progress");
    if (!percentEl && !big) return Promise.resolve();

    return fetchJSON("/stats/averageMood")
        .then(d => {
            const percent = Math.max(0, Math.min(100, Number(d.percent) || 0));
            if (percentEl) percentEl.textContent = percent + "%";
            if (big) big.textContent = percent + "%";
            if (ring) {
                const circumference = 282;
                ring.style.strokeDashoffset = String(circumference - (circumference * percent / 100));
            }
        })
        .catch(() => {
            if (percentEl) percentEl.textContent = "0%";
            if (big) big.textContent = "0%";
        });
}

function updateWeeklyChart() {
    const container = document.getElementById("weeklyChart");
    if (!container) return Promise.resolve();

    return fetchJSON("/stats/weeklyMood")
        .then(rows => {
            container.innerHTML = "";
            if (!rows.length) return;

            rows.forEach(m => {
                const bar = document.createElement("div");
                bar.className = "bar";

                const inner = document.createElement("div");
                inner.className = "bar-inner";
                inner.style.height = Math.min(100, Number(m.level || 0) * 10) + "%";

                const label = document.createElement("div");
                label.className = "bar-label";
                label.innerText = m.mood || m.label || "-";

                bar.appendChild(inner);
                bar.appendChild(label);
                container.appendChild(bar);
            });
        })
        .catch(() => {
            container.innerHTML = "";
        });
}

function calculateWeeklyAverage() {
    return fetchAnalytics("/api/analytics/trends")
        .then(data => {
            if (!data || !data.values || data.values.length === 0) return 0;
            const sum = data.values.reduce((a, b) => a + b, 0);
            return Math.round(sum / data.values.length);
        })
        .catch(() => 0);
}

// ─── Java Analytics Integration ─────────────────────────────────

function updateAnalyticsDashboard() {
    // Streaks
    fetchAnalytics("/api/analytics/streaks").then(data => {
        if (!data) return;
        const streakEl = document.getElementById("positiveStreak");
        const journalStreakEl = document.getElementById("journalStreak");
        if (streakEl) streakEl.textContent = data.currentPositiveStreak || 0;
        if (journalStreakEl) journalStreakEl.textContent = data.journalStreak || 0;
    });

    // Prediction
    fetchAnalytics("/api/analytics/predict").then(data => {
        if (!data) return;
        const predMoodEl = document.getElementById("predictedMood");
        const predConfEl = document.getElementById("predictionConfidence");
        const predBasisEl = document.getElementById("predictionBasis");
        if (predMoodEl) predMoodEl.textContent = data.predictedMood || "--";
        if (predConfEl) predConfEl.textContent = data.confidence ? Math.round(data.confidence * 100) + "%" : "--";
        if (predBasisEl) predBasisEl.textContent = data.basedOn || "";
    });

    // Trends
    fetchAnalytics("/api/analytics/trends").then(data => {
        if (!data) return;
        const trendEl = document.getElementById("moodTrend");
        if (trendEl) {
            const trendIcons = { improving: "📈", declining: "📉", stable: "➡️" };
            trendEl.textContent = `${trendIcons[data.trend] || "➡️"} ${data.trend || "stable"}`;
        }
    });

    // Summary report
    fetchAnalytics("/api/analytics/weekly-report").then(data => {
        if (!data) return;
        const insightsEl = document.getElementById("analyticsInsights");
        if (insightsEl && data.insights && data.insights.length > 0) {
            insightsEl.innerHTML = data.insights
                .map(i => `<div class="insight-item">💡 ${i}</div>`)
                .join("");
        }
    });
}

function updateDashboard() {
    return Promise.all([
        updateLatestMood(),
        updateMostFrequentMood(),
        updateMoodScore(),
        updateSuggestion(),
        updateWeeklyChart(),
        updateJournalCount(),
        checkCrisisStatus()
    ]).then(() => {
        // Load analytics data (non-blocking — if Java service is down, dashboard still works)
        updateAnalyticsDashboard();
    }).catch(() => {});
}

// ═══════════════════════════════════════════════════════════════
// AI CHATBOT (Python + Gemini LLM)
// ═══════════════════════════════════════════════════════════════

async function sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message) return;
    const chatBox = document.getElementById("chat-messages");

    // Create user bubble
    const userDiv = document.createElement("div");
    userDiv.className = "user-msg";
    userDiv.innerText = message;
    chatBox.appendChild(userDiv);
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Show typing indicator
    const typingDiv = document.createElement("div");
    typingDiv.className = "bot-msg typing-indicator";
    typingDiv.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch(`${CHATBOT_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        const data = await response.json();

        // Remove typing indicator
        typingDiv.remove();

        const botDiv = document.createElement("div");
        botDiv.className = "bot-msg";

        // Add emotion badge if available
        if (data.emotion && data.emotion !== "neutral" && data.emotion !== "greeting" && data.emotion !== "farewell") {
            const badge = document.createElement("span");
            badge.className = `emotion-badge emotion-${data.emotion}`;
            badge.textContent = data.emotion;
            botDiv.appendChild(badge);
            botDiv.appendChild(document.createElement("br"));
        }

        botDiv.appendChild(document.createTextNode(data.response));

        // Show source indicator (Gemini vs Template)
        if (data.source === "gemini") {
            const srcTag = document.createElement("span");
            srcTag.className = "source-tag gemini-tag";
            srcTag.textContent = "✨ AI";
            botDiv.appendChild(srcTag);
        }

        chatBox.appendChild(botDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
        typingDiv.remove();
        const botDiv = document.createElement("div");
        botDiv.className = "bot-msg";
        botDiv.innerText = "Unable to connect to AI server.";
        chatBox.appendChild(botDiv);
    }
}

function initDashboard() {
    cachedSuggestion = null;
    updateDashboard();
}

// ─── Chatbot UI Init ────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("chat-toggle");
    const chatbot = document.getElementById("chatbot");
    const closeBtn = document.getElementById("chat-close");
    const sendBtn = document.getElementById("sendBtn");
    if (!toggle || !chatbot || !closeBtn || !sendBtn) return;
    chatbot.classList.add("hidden");
    toggle.style.display = "block";
    toggle.addEventListener("click", function () {
        chatbot.classList.remove("hidden");
        toggle.style.display = "none";
    });
    closeBtn.addEventListener("click", function () {
        chatbot.classList.add("hidden");
        toggle.style.display = "block";
        document.getElementById("chat-messages").innerHTML = "";
    });
    sendBtn.addEventListener("click", sendMessage);

    // Send on Enter key
    const chatInput = document.getElementById("chat-input");
    if (chatInput) {
        chatInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") sendMessage();
        });
    }
});

// ─── Page Load Initialization ───────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
    const page = window.location.pathname.toLowerCase();
    const isMoodPage = page.endsWith("/mood.html") || page.endsWith("mood.html");
    const isDashboardPage = page.endsWith("/dashboard.html") || page.endsWith("dashboard.html");
    if (isMoodPage) {
        renderMoods();
    }
    if (isDashboardPage) {
        initDashboard();
        window.addEventListener("focus", initDashboard);
        document.addEventListener("visibilitychange", () => {
            if (!document.hidden) initDashboard();
        }); 
    }
});

window.addEventListener("pageshow", function (event) {
    const page = window.location.pathname.toLowerCase();
    const isDashboardPage =
        page.endsWith("/dashboard.html") || page.endsWith("dashboard.html");
    if (isDashboardPage) {
        if (event.persisted) {
            location.reload();
        } else {
            cachedSuggestion = null;
            updateDashboard();
        }
    }
});

function openEQ() {
    window.location.href = "eq.html";
}
