# CEREVIA 2.0 – AI-Powered Mental Wellness Platform 🧠✨

![CEREVIA Header](https://via.placeholder.com/1000x300/090a0f/ffffff?text=CEREVIA+2.0+-+Mental+Wellness+Microservices)

CEREVIA is a comprehensive, microservices-based mental health and wellness platform. It features a stunning 3D glassmorphic user interface, secure local data storage, and an empathetic AI chatbot powered by Google Gemini 2.0 and VADER Sentiment Analysis.

---

## 📸 Screenshots

*(Add your screenshots here on GitHub by dragging and dropping them!)*

| **Lamp Login Interface** | **3D Glassmorphic Dashboard** |
| :---: | :---: |
| ![Login Placeholder](https://via.placeholder.com/400x250/1c1c28/ffffff?text=Add+Login+Screenshot+Here) | ![Dashboard Placeholder](https://via.placeholder.com/400x250/1c1c28/ffffff?text=Add+Dashboard+Screenshot+Here) |

| **AI Wellness Chatbot** | **Mood & Journal Tracking** |
| :---: | :---: |
| ![Chat Placeholder](https://via.placeholder.com/400x250/1c1c28/ffffff?text=Add+Chat+Screenshot+Here) | ![Journal Placeholder](https://via.placeholder.com/400x250/1c1c28/ffffff?text=Add+Journal+Screenshot+Here) |

---

## 🚀 Features

- **3D Glassmorphic UI:** Built entirely from scratch using pure HTML/CSS/JS without heavy frameworks. Includes physics-based animations, 3D tilt effects, and an interactive "Lamp" login screen.
- **AI-Powered Therapy Chatbot:** Uses Google Gemini 2.0 and VADER NLP to understand user sentiment, provide cognitive reframing techniques, and detect crisis keywords for emergency intervention.
- **Dynamic Wellness Engine:** Curates real-time wellness plans, breathing exercises, and yoga/meditation videos based on the user's logged emotional state.
- **Secure Data Storage:** Custom SQLite backend featuring XOR encryption to ensure total privacy for sensitive journal entries.
- **Advanced Analytics:** Java Spring Boot engine that calculates mood streaks, dominant emotions, and predictive wellness reports.

---

## 🛠️ Tech Stack & Architecture

CEREVIA operates on a locally-hosted **Microservices Architecture**:

1. **Frontend (UI):** Vanilla HTML5, CSS3 (3D CSS, Glassmorphism), JavaScript
2. **Core Backend (C++):** Custom HTTP server using WinSock2 (Port 5000). Handles user auth, SQLite database routing, and encryption.
3. **AI Chatbot (Python):** Flask microservice (Port 5001) integrating Google Gemini API and `vaderSentiment`.
4. **Analytics Engine (Java):** Spring Boot microservice (Port 8080) for data analysis.

---

## ⚙️ How to Run Locally

Because CEREVIA uses a microservices architecture, you need to start the backend servers before using the frontend.

### 1. Start the C++ Core Server
```bash
cd backend/build/Debug
./backend.exe
```
*(Runs on http://localhost:5000)*

### 2. Start the Python AI Chatbot
Ensure you have your Gemini API key set in `ai_chatbot/config.py`.
```bash
cd ai_chatbot
python app.py
```
*(Runs on http://localhost:5001)*

### 3. Start the Java Analytics Server
```bash
cd analytics
mvn spring-boot:run
```
*(Runs on http://localhost:8080)*

### 4. Launch the Frontend
Simply open `frontend/index.html` in any modern web browser (Edge, Chrome, Firefox). No local web server is strictly required for the frontend!

---

## 🔒 Privacy First
All journal entries and mood logs are stored strictly locally in `database/mental_health.db` using custom XOR encryption. Your data never leaves your machine unless you are interacting with the AI Chatbot.
