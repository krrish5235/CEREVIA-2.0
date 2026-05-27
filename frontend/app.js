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

//Settting up the link on local server before hand so that it connects to the backend correctly and on the correct port
const API_URL = "http://127.0.0.1:5000";

async function fetchJSON(path, options = {}) {
    const res = await fetch(`${API_URL}${path}`, options);
    if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
    }
    return res.json();
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

// Resets mood history from backend database
// Calls backend API to delete all mood records
function resetMood() {
    if (!confirm("Delete all mood history?")) return;
    fetch(`${API_URL}/mood/reset`, { method: "POST" })
        .then(r => r.json())
        .then(d => {
            showPopup("Mood history cleared ✅");
            loadMoods();
        });
}

// Resets journal history from backend database
// Calls backend API to delete all journal entries
function resetJournal() {
    if (!confirm("Delete all journal entries?")) return;
    fetch(`${API_URL}/journal/reset`, { method: "POST" })
        .then(r => r.json())
        .then(d => {
            showPopup("Journal cleared ✅");
            loadJournal();
        });
}

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
// Redirects user to call that number
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

// Toggles dark/light theme from settings page
// Saves theme preference in localStorage
function toggleThemeFromSettings() {
    const isDark = document.body.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    showPopup(isDark ? "Dark Mode Enabled 🌙" : "Light Mode Enabled ☀️");
}

// Sets loggedIn status in localStorage
function restoreTheme() {
    const theme = localStorage.getItem("theme");
    if (theme === "dark") {
        document.body.classList.add("dark");
    } else {
        document.body.classList.remove("dark");
    }
}

function syncThemeControls() {
    const isDark = document.body.classList.contains("dark");
    document.querySelectorAll("#darkSwitch").forEach(control => {
        control.checked = isDark;
    });
}

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

function toggleThemeFromSettings() {
    const nextTheme = document.body.classList.contains("dark") ? "light" : "dark";
    setTheme(nextTheme);
    showPopup(nextTheme === "dark" ? "Dark Mode Enabled ðŸŒ™" : "Light Mode Enabled â˜€ï¸");
}

function restoreTheme() {
    applyTheme(localStorage.getItem("theme") === "dark" ? "dark" : "light");
}

window.addEventListener("storage", event => {
    if (event.key === "theme") {
        applyTheme(event.newValue === "dark" ? "dark" : "light");
    }
});

// Sets loggedIn status in localStorage
function setLoggedIn(v) {
    localStorage.setItem("loggedIn", v ? "true" : "false");
}

// Checks if user is logged in
// Returns boolean
function isLoggedIn() {
    return localStorage.getItem("loggedIn") === "true";
}

// Ensures authentication before accessing protected pages
// Redirects to login if not authenticated
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

// Ensures authentication before accessing protected pages
// Redirects to login if not authenticated
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
// Sends PIN to backend and authenticates user
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

// Adds new mood entry locally in localStorage
// Updates dashboard immediately
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

// Renders all mood entries from localStorage
// Displays them on mood page
function renderMoods() {
    loadMoods();
}

function calculateWeeklyAverage() {
    return 0;
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
        showPopup("Journal saved ?");
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

function getAllMoods() {
    return [];
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

function updateDashboard() {
    return Promise.all([
        updateLatestMood(),
        updateMostFrequentMood(),
        updateMoodScore(),
        updateSuggestion(),
        updateWeeklyChart(),
        updateJournalCount(),
        checkCrisisStatus()
    ]).catch(() => {});
}

// =============================================================================================================================
//=====================================================AI CHATBOT===============================================================
// Sends message to AI backend server
// Handles chatbot communication
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
    try {
        const response = await fetch("http://127.0.0.1:5001/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        const botDiv = document.createElement("div");
        botDiv.className = "bot-msg";
        botDiv.innerText = data.response;
        chatBox.appendChild(botDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
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
// Handles chatbot open/close behavior
// Initializes chatbot UI state
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
});

// Runs on page load
// Renders moods and updates dashboard
window.addEventListener("DOMContentLoaded", () => {
    const page = window.location.pathname.toLowerCase();
    const isMoodPage = page.endsWith("/mood.html") || page.endsWith("mood.html");
    const isDashboardPage = page.endsWith("/dashboard.html") || page.endsWith("dashboard.html");
    if (isMoodPage) {
        renderMoods();
    }
    if (isDashboardPage) {
    initDashboard(); // load immediately
    // When user switches back to tab
    window.addEventListener("focus", initDashboard);

    // When page becomes visible again
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
        // Force refresh when returning from browser back/forward cache
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
