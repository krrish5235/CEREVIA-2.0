"""
CEREVIA AI Chatbot — Main Application
Flask microservice providing:
  - /chat         → AI-powered conversation with Gemini LLM + NLP emotion detection
  - /chat/analyze → Detailed NLP emotion breakdown for a given message
  - /chat/history → Retrieve current session conversation history
  - /chat/reset   → Clear conversation history

Tech Stack: Python, Flask, VADER Sentiment (NLP), Google Gemini (Generative AI / LLM API)
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from sentiment_model import analyze_sentiment
from emotion_engine import detect_emotion, detect_emotion_simple
from response_generator import generate_response, generate_response_simple
from config import (
    CRISIS_KEYWORDS, CRISIS_RESPONSE,
    CHATBOT_PORT, MAX_CONVERSATION_HISTORY
)
import logging
import os

# ─── App Setup ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cerevia-secret-key-2026")
CORS(app, supports_credentials=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cerevia-chatbot")

# In-memory conversation store (simple, single-user)
# For production, use Redis or database-backed sessions
conversation_store = []


# ─── Helper Functions ───────────────────────────────────────────────────────
def _get_conversation_history():
    """Get the current conversation history."""
    return conversation_store[-MAX_CONVERSATION_HISTORY:]


def _add_to_history(role, content):
    """Add a message to conversation history."""
    conversation_store.append({"role": role, "content": content})
    # Trim to max size
    while len(conversation_store) > MAX_CONVERSATION_HISTORY:
        conversation_store.pop(0)


def _check_crisis(message):
    """Check if message contains crisis keywords."""
    message_lower = message.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            return True, keyword
    return False, None


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route("/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint.
    
    Request:  { "message": "I feel so anxious today" }
    Response: {
        "emotion": "anxious",
        "response": "It sounds like anxiety is weighing on you...",
        "confidence": 0.85,
        "source": "gemini",
        "analysis": { "method": "keyword_weighted", "scores": {...} }
    }
    """
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data.get("message", "").strip()

    # Handle empty messages
    if not message:
        return jsonify({
            "emotion": "neutral",
            "response": "I'm here whenever you're ready to talk. 💙",
            "confidence": 1.0,
            "source": "template",
            "analysis": {"method": "empty_input"}
        })

    # ─── Stage 1: Crisis Safety Check (Always First) ────────────────
    is_crisis, matched_keyword = _check_crisis(message)
    if is_crisis:
        logger.warning("🚨 Crisis keyword detected: '%s'", matched_keyword)
        _add_to_history("user", message)
        _add_to_history("assistant", CRISIS_RESPONSE)
        return jsonify({
            "emotion": "crisis",
            "response": CRISIS_RESPONSE,
            "confidence": 1.0,
            "source": "safety_filter",
            "analysis": {"method": "crisis_keyword", "matched": matched_keyword}
        })

    # ─── Stage 2: NLP Emotion Detection ─────────────────────────────
    sentiment_score = analyze_sentiment(message)
    emotion, confidence, analysis = detect_emotion(sentiment_score, message)

    # Handle mixed emotions (e.g., "I was happy but now I'm sad")
    if "but" in message.lower() or "however" in message.lower():
        if sentiment_score < 0:
            emotion = "mild_sad"
            analysis["mixed_emotion"] = True
        elif sentiment_score > 0:
            emotion = "happy"
            analysis["mixed_emotion"] = True

    # ─── Stage 3: Generate Response (Gemini → Template Fallback) ────
    history = _get_conversation_history()
    response_text, source = generate_response(
        emotion=emotion,
        message=message,
        confidence=confidence,
        conversation_history=history
    )

    # ─── Stage 4: Update Conversation Memory ────────────────────────
    _add_to_history("user", message)
    _add_to_history("assistant", response_text)

    logger.info(
        "💬 [%s] emotion=%s conf=%.2f source=%s msg='%s'",
        analysis.get("method", "unknown"), emotion, confidence, source,
        message[:50]
    )

    return jsonify({
        "emotion": emotion,
        "response": response_text,
        "confidence": round(confidence, 2),
        "source": source,
        "analysis": analysis
    })


@app.route("/chat/analyze", methods=["POST"])
def analyze():
    """
    Detailed NLP emotion analysis endpoint.
    Returns full breakdown without generating a response.
    
    Request:  { "message": "I feel lost and overwhelmed" }
    Response: {
        "sentiment": { "compound": -0.45, "pos": 0.0, "neg": 0.55, "neu": 0.45 },
        "emotion": "deep_sad",
        "confidence": 0.82,
        "analysis": { ... },
        "keywords_detected": { "deep_sad": ["lost"], "anxious": ["overwhelmed"] }
    }
    """
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    # Full sentiment analysis
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(message)

    # Emotion detection with full details
    emotion, confidence, analysis = detect_emotion(sentiment_scores["compound"], message)

    # Find matched keywords for transparency
    text_lower = message.lower()
    from emotion_engine import (
        DEEP_SAD_KEYWORDS, ANXIOUS_KEYWORDS, HAPPY_KEYWORDS, ANGRY_KEYWORDS
    )
    keywords_detected = {
        "deep_sad": [k for k in DEEP_SAD_KEYWORDS if k in text_lower],
        "anxious": [k for k in ANXIOUS_KEYWORDS if k in text_lower],
        "happy": [k for k in HAPPY_KEYWORDS if k in text_lower],
        "angry": [k for k in ANGRY_KEYWORDS if k in text_lower],
    }
    # Remove empty categories
    keywords_detected = {k: v for k, v in keywords_detected.items() if v}

    return jsonify({
        "sentiment": {
            "compound": sentiment_scores["compound"],
            "positive": sentiment_scores["pos"],
            "negative": sentiment_scores["neg"],
            "neutral": sentiment_scores["neu"]
        },
        "emotion": emotion,
        "confidence": round(confidence, 2),
        "analysis": analysis,
        "keywords_detected": keywords_detected
    })


@app.route("/chat/history", methods=["GET"])
def get_history():
    """Return current conversation history."""
    return jsonify({
        "history": _get_conversation_history(),
        "count": len(conversation_store)
    })


@app.route("/chat/reset", methods=["POST"])
def reset_history():
    """Clear conversation history."""
    conversation_store.clear()
    logger.info("🗑️ Conversation history cleared")
    return jsonify({"message": "Conversation history cleared", "success": True})


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    from response_generator import gemini_available
    return jsonify({
        "status": "ok",
        "service": "cerevia-chatbot",
        "gemini_enabled": gemini_available,
        "conversation_length": len(conversation_store)
    })


# ─── Yoga Videos Endpoint ───────────────────────────────────────────────────

YOGA_VIDEOS = {
    "morning": {
        "title": "🌅 Morning Yoga",
        "description": "Start your day with energy and clarity",
        "videos": [
            {"title": "10-Min Morning Yoga for Beginners", "url": "https://www.youtube.com/watch?v=g_tea8ZNk5A", "duration": "10 min", "level": "Beginner"},
            {"title": "Morning Yoga Flow — Full Body Stretch", "url": "https://www.youtube.com/watch?v=4pKly2JojMw", "duration": "20 min", "level": "All Levels"},
            {"title": "Sunrise Yoga — Energizing Routine", "url": "https://www.youtube.com/watch?v=UEEsdXn8oG8", "duration": "15 min", "level": "Beginner"},
            {"title": "5-Min Wake Up Yoga in Bed", "url": "https://www.youtube.com/watch?v=aGxN00SxCVw", "duration": "5 min", "level": "Easy"},
        ]
    },
    "stress_relief": {
        "title": "🧘 Stress Relief",
        "description": "Release tension and find inner calm",
        "videos": [
            {"title": "Yoga for Stress Relief — 20 Min", "url": "https://www.youtube.com/watch?v=hJbRpHZr_d0", "duration": "20 min", "level": "All Levels"},
            {"title": "Relaxing Yoga for Anxiety & Stress", "url": "https://www.youtube.com/watch?v=COp7BR_Dvps", "duration": "25 min", "level": "Beginner"},
            {"title": "Yoga to Calm Your Mind", "url": "https://www.youtube.com/watch?v=bJJWArKlKSs", "duration": "15 min", "level": "All Levels"},
            {"title": "Chair Yoga for Stress at Work", "url": "https://www.youtube.com/watch?v=tAUf7aajBWE", "duration": "12 min", "level": "Easy"},
        ]
    },
    "sleep": {
        "title": "🌙 Sleep & Relaxation",
        "description": "Wind down and prepare for restful sleep",
        "videos": [
            {"title": "Bedtime Yoga — Deep Relaxation", "url": "https://www.youtube.com/watch?v=BiWDsfZ3zbo", "duration": "20 min", "level": "All Levels"},
            {"title": "Yoga Nidra — Guided Sleep Meditation", "url": "https://www.youtube.com/watch?v=M0u9GST_j3s", "duration": "30 min", "level": "Easy"},
            {"title": "Gentle Night Yoga for Better Sleep", "url": "https://www.youtube.com/watch?v=v7SN-d4qXx0", "duration": "15 min", "level": "Beginner"},
            {"title": "Full Body Stretch Before Bed", "url": "https://www.youtube.com/watch?v=sTANio_2E0Q", "duration": "10 min", "level": "Easy"},
        ]
    },
    "anxiety": {
        "title": "💆 Anxiety Relief",
        "description": "Calm your nervous system with gentle movement",
        "videos": [
            {"title": "Yoga for Anxiety — Ground Yourself", "url": "https://www.youtube.com/watch?v=hJbRpHZr_d0", "duration": "20 min", "level": "Beginner"},
            {"title": "Breathing Yoga for Panic & Anxiety", "url": "https://www.youtube.com/watch?v=8VwufJrUhic", "duration": "15 min", "level": "Easy"},
            {"title": "Restorative Yoga for Anxious Minds", "url": "https://www.youtube.com/watch?v=Nw2oBIrQGLo", "duration": "25 min", "level": "All Levels"},
            {"title": "5-Min Emergency Calm Down Yoga", "url": "https://www.youtube.com/watch?v=4C-gxOE0j7s", "duration": "5 min", "level": "Easy"},
        ]
    },
    "energy": {
        "title": "⚡ Energy Boost",
        "description": "Recharge with dynamic yoga flows",
        "videos": [
            {"title": "Power Yoga — Full Body Energy", "url": "https://www.youtube.com/watch?v=9kOCY0KNByw", "duration": "30 min", "level": "Intermediate"},
            {"title": "Quick Energy Boost Yoga Flow", "url": "https://www.youtube.com/watch?v=Eml2xnoLpYE", "duration": "10 min", "level": "All Levels"},
            {"title": "Sun Salutation — Traditional Flow", "url": "https://www.youtube.com/watch?v=73sjOu0g58M", "duration": "15 min", "level": "Beginner"},
            {"title": "Vinyasa Flow for Strength", "url": "https://www.youtube.com/watch?v=9kOCY0KNByw", "duration": "25 min", "level": "Intermediate"},
        ]
    },
    "meditation": {
        "title": "🧠 Guided Meditation",
        "description": "Mindfulness sessions for mental clarity",
        "videos": [
            {"title": "10-Min Mindfulness Meditation", "url": "https://www.youtube.com/watch?v=ZToicYcHIqU", "duration": "10 min", "level": "Easy"},
            {"title": "Body Scan Meditation for Beginners", "url": "https://www.youtube.com/watch?v=15q-N-_kkrU", "duration": "15 min", "level": "Beginner"},
            {"title": "Loving Kindness Meditation", "url": "https://www.youtube.com/watch?v=sz7cpV7ERsM", "duration": "12 min", "level": "All Levels"},
            {"title": "Gratitude Meditation — 5 Min Daily", "url": "https://www.youtube.com/watch?v=O-6f5wQXSu8", "duration": "5 min", "level": "Easy"},
        ]
    }
}


@app.route("/yoga/videos", methods=["GET"])
def get_yoga_videos():
    """
    Get curated yoga and wellness videos.
    Optional query params: ?category=stress_relief&mood=anxious
    """
    category = request.args.get("category", "").lower()
    mood = request.args.get("mood", "").lower()

    mood_to_category = {
        "anxious": "anxiety", "stressed": "stress_relief",
        "sad": "sleep", "angry": "stress_relief",
        "happy": "energy", "calm": "meditation", "neutral": "morning",
    }

    if mood and mood in mood_to_category:
        category = mood_to_category[mood]

    if category and category in YOGA_VIDEOS:
        return jsonify({
            "category": category,
            "data": YOGA_VIDEOS[category],
            "total": len(YOGA_VIDEOS[category]["videos"])
        })

    return jsonify({
        "categories": list(YOGA_VIDEOS.keys()),
        "data": YOGA_VIDEOS,
        "total_categories": len(YOGA_VIDEOS),
        "total_videos": sum(len(v["videos"]) for v in YOGA_VIDEOS.values())
    })


# ─── Daily Wellness Tips ────────────────────────────────────────────────────

import random

WELLNESS_TIPS = {
    "general": [
        {"tip": "Take 5 deep breaths right now. In for 4, hold for 4, out for 6.", "icon": "🫁", "category": "Breathing"},
        {"tip": "Step outside for 5 minutes. Sunlight boosts serotonin naturally.", "icon": "☀️", "category": "Movement"},
        {"tip": "Write 3 things you're grateful for today, no matter how small.", "icon": "📝", "category": "Journaling"},
        {"tip": "Drink a full glass of water. Dehydration affects your mood.", "icon": "💧", "category": "Self-Care"},
        {"tip": "Put your phone down for 15 minutes. Your mind needs a break.", "icon": "📵", "category": "Digital Detox"},
        {"tip": "Text someone you care about. Connection is medicine.", "icon": "💬", "category": "Connection"},
        {"tip": "Do 10 stretches at your desk. Your body holds your emotions.", "icon": "🧘", "category": "Movement"},
        {"tip": "Listen to a song that makes you feel alive.", "icon": "🎵", "category": "Music"},
        {"tip": "Name 5 things you can see, 4 you can hear, 3 you can touch.", "icon": "🌿", "category": "Grounding"},
        {"tip": "It's okay to rest. Productivity does not equal your worth.", "icon": "😴", "category": "Rest"},
    ],
    "anxious": [
        {"tip": "Try the 5-4-3-2-1 grounding technique. Name 5 things you see.", "icon": "👁️", "category": "Grounding"},
        {"tip": "Place your hand on your chest. Feel your heartbeat. You are safe.", "icon": "❤️", "category": "Self-Soothing"},
        {"tip": "Breathe in for 4, hold for 7, exhale for 8. Repeat 3 times.", "icon": "🫁", "category": "Breathing"},
    ],
    "sad": [
        {"tip": "Go for a 10-minute walk. Movement shifts brain chemistry.", "icon": "🚶", "category": "Movement"},
        {"tip": "Allow yourself to feel sad. It's not weakness, it's being human.", "icon": "💙", "category": "Validation"},
        {"tip": "Watch something that made you laugh before. Laughter heals.", "icon": "😂", "category": "Mood Boost"},
    ],
    "angry": [
        {"tip": "Splash cold water on your face. It triggers the dive reflex.", "icon": "🧊", "category": "Cooling"},
        {"tip": "Write down what's making you angry. Externalizing helps.", "icon": "📝", "category": "Processing"},
        {"tip": "Do 20 jumping jacks. Channel that energy into movement.", "icon": "🏃", "category": "Movement"},
    ],
    "happy": [
        {"tip": "Savor this moment. Take a mental snapshot of how you feel.", "icon": "📸", "category": "Mindfulness"},
        {"tip": "Share your joy with someone. Happiness multiplies when shared.", "icon": "🎉", "category": "Connection"},
        {"tip": "Write down what made you happy today. Build a joy archive.", "icon": "📖", "category": "Journaling"},
    ]
}


@app.route("/wellness/tips", methods=["GET"])
def get_wellness_tips():
    """Get daily wellness tips. Optional: ?mood=anxious for mood-specific tips."""
    mood = request.args.get("mood", "general").lower()
    count = int(request.args.get("count", 3))
    tips = WELLNESS_TIPS.get(mood, []) + WELLNESS_TIPS["general"]
    selected = random.sample(tips, min(count, len(tips)))
    return jsonify({"mood": mood, "tips": selected, "count": len(selected)})


# ─── AI Wellness Recommendation ────────────────────────────────────────────

@app.route("/wellness/recommend", methods=["POST"])
def wellness_recommend():
    """
    Use Gemini AI to generate a personalized wellness plan.
    Request: { "mood": "anxious", "context": "I have a big exam tomorrow" }
    """
    from response_generator import gemini_model, gemini_available

    data = request.json or {}
    mood = data.get("mood", "neutral")
    context = data.get("context", "")

    if not gemini_available:
        return jsonify({
            "plan": {
                "activity": "Try a 10-minute breathing exercise",
                "yoga_type": "stress_relief",
                "breathing": "Box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s",
                "affirmation": "I am doing my best, and that is enough",
                "music_suggestion": "Calm ambient or lo-fi music",
                "duration": "15 minutes"
            },
            "source": "template"
        })

    try:
        prompt = f"""Based on this person's current state, create a short personalized wellness plan.

Mood: {mood}
Context: {context or 'No additional context'}

Return ONLY a JSON object (no markdown, no code fences) with these fields:
- "activity": one specific activity they should do right now (1 sentence)
- "yoga_type": one of: morning, stress_relief, sleep, anxiety, energy, meditation
- "breathing": a specific breathing technique with counts (1 sentence)
- "affirmation": a personalized affirmation for their situation (1 sentence)
- "music_suggestion": type of music that would help (1 sentence)
- "duration": suggested wellness session length like "15 minutes"
"""
        response = gemini_model.generate_content(prompt)
        if response and response.text:
            import json as json_lib
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            plan = json_lib.loads(text)

            yoga_type = plan.get("yoga_type", "stress_relief")
            if yoga_type in YOGA_VIDEOS:
                plan["recommended_videos"] = YOGA_VIDEOS[yoga_type]["videos"][:2]

            return jsonify({"plan": plan, "source": "gemini"})

    except Exception as e:
        logger.warning("⚠️ Wellness recommendation failed: %s", e)

    return jsonify({
        "plan": {
            "activity": "Take a 10-minute walk outside",
            "yoga_type": "stress_relief",
            "breathing": "Box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s",
            "affirmation": "I am doing my best, and that is enough",
            "music_suggestion": "Calm ambient or lo-fi music",
            "duration": "15 minutes"
        },
        "source": "template"
    })


# ─── Entry Point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("🧠 CEREVIA AI Chatbot starting on port %d", CHATBOT_PORT)
    logger.info("   Tech: Python + Flask + VADER NLP + Google Gemini LLM")
    logger.info("   Endpoints: /chat, /yoga/videos, /wellness/tips, /wellness/recommend")
    app.run(port=CHATBOT_PORT, debug=True)
