"""
CEREVIA AI Chatbot — Response Generator
Uses the NEW google-genai SDK for Gemini LLM responses.
Falls back to curated templates if Gemini is unavailable.
"""

import json
import random
import logging
from config import (
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_SYSTEM_PROMPT,
    GEMINI_TEMPERATURE, GEMINI_MAX_TOKENS, GEMINI_TOP_P,
    TEMPLATES_PATH
)

logger = logging.getLogger(__name__)

# ─── Initialize Gemini (New SDK) ────────────────────────────────────────────
gemini_client = None
gemini_available = False
gemini_model = None  # exposed for wellness/recommend endpoint

if GEMINI_API_KEY:
    try:
        from google import genai
        from google.genai import types

        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        gemini_available = True
        logger.info("✅ Gemini LLM initialized (google-genai SDK, model: %s)", GEMINI_MODEL)
    except Exception as e:
        logger.warning("⚠️ Gemini initialization failed: %s. Using template fallback.", e)
else:
    logger.info("ℹ️ No GEMINI_API_KEY set. Using template-based responses only.")


# ─── Load Templates ─────────────────────────────────────────────────────────
def _load_templates():
    """Load response templates from JSON file."""
    try:
        with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        try:
            with open("templates.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("❌ templates.json not found!")
            return {"neutral": ["I'm here for you. Tell me more."]}


templates = _load_templates()


# ─── Gemini Response Generation ─────────────────────────────────────────────
def _generate_gemini_response(message, emotion, confidence, conversation_history):
    """
    Generate a response using Google Gemini LLM (new google-genai SDK).
    """
    if not gemini_available or not gemini_client:
        return None

    try:
        from google.genai import types

        # Build context-rich prompt
        context_parts = []

        # Add conversation history for context
        if conversation_history:
            context_parts.append("Recent conversation:")
            for msg in conversation_history[-6:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context_parts.append(f"  {role}: {content}")
            context_parts.append("")

        # Add emotion context
        context_parts.append(
            f"[Emotion Analysis] Detected: {emotion} (confidence: {confidence:.0%})"
        )
        context_parts.append(f"[User Message] {message}")
        context_parts.append("")
        context_parts.append(
            "Respond with empathy and give actionable advice. "
            "Keep it to 2-4 sentences. Don't mention the emotion analysis."
        )

        full_prompt = "\n".join(context_parts)

        # Generate with new SDK
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_SYSTEM_PROMPT,
                temperature=GEMINI_TEMPERATURE,
                max_output_tokens=GEMINI_MAX_TOKENS,
                top_p=GEMINI_TOP_P,
            ),
        )

        if response and response.text:
            generated = response.text.strip()
            if len(generated) > 5:
                logger.info("🤖 Gemini response generated successfully")
                return generated

    except Exception as e:
        logger.warning("⚠️ Gemini generation failed: %s. Falling back to templates.", e)

    return None


# ─── Gemini direct call (for wellness/recommend endpoint) ───────────────────
class _GeminiModelProxy:
    """Proxy object so app.py's wellness/recommend endpoint can call generate_content."""
    def generate_content(self, prompt):
        if not gemini_available or not gemini_client:
            return None
        try:
            from google.genai import types
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=400,
                ),
            )
            return response
        except Exception as e:
            logger.warning("⚠️ Gemini proxy call failed: %s", e)
            return None

gemini_model = _GeminiModelProxy()


# ─── Template Response Generation ───────────────────────────────────────────
def _generate_template_response(emotion):
    """Generate a response from curated templates."""
    if emotion not in templates:
        emotion = "random"
    responses = templates.get(emotion, templates.get("neutral", ["I'm here for you."]))
    return random.choice(responses)


# ─── Public API ─────────────────────────────────────────────────────────────
def generate_response(emotion, message="", confidence=0.5, conversation_history=None):
    """
    Generate an empathetic response using Gemini LLM with template fallback.
    Returns: (response_text, source)
    """
    if conversation_history is None:
        conversation_history = []

    # Skip Gemini for simple greetings/farewells
    if emotion in ("greeting", "farewell"):
        return _generate_template_response(emotion), "template"

    # Try Gemini first
    gemini_response = _generate_gemini_response(
        message, emotion, confidence, conversation_history
    )
    if gemini_response:
        return gemini_response, "gemini"

    # Fallback to templates
    return _generate_template_response(emotion), "template"


def generate_response_simple(emotion):
    """Backward-compatible wrapper."""
    response, _ = generate_response(emotion)
    return response