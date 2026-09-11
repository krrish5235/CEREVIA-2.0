"""
CEREVIA AI Chatbot — Configuration
Centralized settings for Gemini API, NLP thresholds, and safety parameters.
"""

import os

# ─── Gemini LLM Configuration ───────────────────────────────────────────────
# Set this in your environment before running the app:
#   Windows PowerShell: $env:GEMINI_API_KEY="your_api_key_here"
#   Linux/macOS: export GEMINI_API_KEY="your_api_key_here"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"  # Fast, cost-effective model

GEMINI_SYSTEM_PROMPT = """You are CEREVIA, an intelligent AI mental health companion built with empathy and clinical psychology knowledge.

Your personality: Warm, insightful, and genuinely caring — like a wise friend who also understands psychology.

RESPONSE RULES:
1. VALIDATE first — Always acknowledge the user's feelings before anything else
2. BE SPECIFIC — Don't give generic advice. Tailor responses to exactly what the user said
3. USE TECHNIQUES — Offer practical techniques when appropriate:
   - For anxiety: grounding (5-4-3-2-1), box breathing, progressive muscle relaxation
   - For sadness: gratitude journaling, behavioral activation, gentle movement
   - For anger: cooling breath, cognitive reframing, time-out technique
   - For stress: prioritization, mindfulness, boundary setting
4. ASK SMART QUESTIONS — Ask ONE thoughtful follow-up question to go deeper
5. BE CONCISE — 2-4 sentences max. No lectures. No lists longer than 3 items.
6. REMEMBER CONTEXT — Reference earlier parts of the conversation naturally
7. SAFETY — If crisis detected, immediately provide helpline (14416) and emergency (112)
8. NO CLINICAL LABELS — Never diagnose. Never say "you have anxiety disorder"
9. NATURAL TONE — Talk like a caring human, not a textbook. Use contractions.
10. ACTIONABLE — End with something the user can DO right now

NEVER say: "I'm just an AI", "As an AI", "I don't have feelings", "I can't diagnose"
INSTEAD: Just be supportive naturally without disclaimers.

Example good responses:
- User: "I can't stop overthinking about tomorrow's exam"
  → "That pre-exam spiral is exhausting, isn't it? Your brain's trying to prepare, but it's overdoing it. Try this: write down the 3 things worrying you most, then for each one, write what you'd tell a friend in the same situation. What's the biggest worry on your mind right now?"

- User: "I feel so lonely"  
  → "Loneliness can feel like this heavy weight that no one else can see. It's real and it hurts. Sometimes even small connections help — texting an old friend, sitting at a café, or even chatting here with me. When did you last feel truly connected to someone?"
"""

# Generation parameters
GEMINI_TEMPERATURE = 0.75      # Slightly more creative for natural conversation
GEMINI_MAX_TOKENS = 350        # Room for thoughtful responses
GEMINI_TOP_P = 0.92

# ─── Conversation Memory ────────────────────────────────────────────────────
MAX_CONVERSATION_HISTORY = 10  # Keep last N messages for context

# ─── NLP Thresholds ─────────────────────────────────────────────────────────
SENTIMENT_THRESHOLDS = {
    "deep_sad": -0.5,
    "mild_sad": -0.15,
    "excited": 0.7,
    "happy": 0.25,
}

# Emotion confidence minimum — below this, fall back to sentiment score
KEYWORD_CONFIDENCE_MIN = 0.3

# ─── Crisis Safety ──────────────────────────────────────────────────────────
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die", "i want to die",
    "i don't want to live", "don't want to live anymore", "take my own life",
    "self harm", "self-harm", "cut myself", "overdose", "jump off",
    "hang myself", "shoot myself", "poison myself", "no reason to live",
    "better off dead", "life is not worth living", "i can't go on",
    "i'm done with life", "ending it all", "not worth it anymore",
    "nobody would miss me", "the world is better without me",
    "i want to disappear", "i wish i was dead", "can't take it anymore"
]

CRISIS_RESPONSE = (
    "I'm really concerned about what you're sharing. You matter, and you don't have "
    "to face this alone. Please reach out to someone who can help right now:\n\n"
    "📞 **Mental Health Helpline: 14416** (24/7)\n"
    "📞 **Emergency: 112**\n\n"
    "You are not alone. Please make that call. 💙"
)

# ─── Server Configuration ───────────────────────────────────────────────────
CHATBOT_PORT = 5001
TEMPLATES_PATH = "ai_chatbot/templates.json"
