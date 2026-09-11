"""
CEREVIA AI Chatbot — Enhanced Emotion Engine
Multi-stage NLP pipeline combining keyword analysis, VADER sentiment,
and confidence scoring for accurate emotion detection.
"""

from sentiment_model import analyze_sentiment
from config import SENTIMENT_THRESHOLDS, KEYWORD_CONFIDENCE_MIN


# ─── Keyword Dictionaries with Weights ──────────────────────────────────────

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

GREETINGS = [
    "hello", "hi", "hey", "good morning", "good evening",
    "good afternoon", "hlo", "hlw", "hiii", "helloo",
    "heyy", "yo", "hi there", "hey there", "namaste",
    "wassup", "what's up", "sup", "hola", "hiya",
    "morning", "evening", "greetings", "hello again",
    "long time no see", "howdy"
]

FAREWELLS = [
    "bye", "goodbye", "see you", "take care",
    "tata", "see ya", "bye bye", "good night",
    "gn", "see you later", "catch you later",
    "farewell", "peace out", "i'm leaving",
    "talk later", "brb", "gotta go",
    "have a good day", "have a nice day",
    "logging off", "signing off"
]

# Weighted keyword groups: (keyword, intensity_weight)
DEEP_SAD_KEYWORDS = {
    "hopeless": 1.0, "meaningless": 1.0, "worthless": 1.0, "empty": 0.8,
    "broken": 0.9, "tired of life": 1.0, "numb": 0.8, "lost": 0.6,
    "no purpose": 1.0, "hate myself": 1.0, "feel useless": 0.9,
    "alone": 0.7, "abandoned": 0.9, "emotionally drained": 0.8,
    "exhausted with life": 0.9, "i give up": 0.9,
    "no one cares": 0.9, "i feel invisible": 0.8,
    "i am a burden": 1.0, "nothing matters": 0.9,
    "feel dead inside": 1.0, "drowning in pain": 1.0,
    "can't go on": 0.9, "life is pointless": 1.0,
    "i feel shattered": 0.9, "crying": 0.6, "tears": 0.5,
    "depressed": 0.9, "depression": 0.9, "miserable": 0.8
}

ANXIOUS_KEYWORDS = {
    "anxious": 0.9, "nervous": 0.7, "panic": 1.0, "worried": 0.7,
    "stress": 0.7, "stressed": 0.7, "overthinking": 0.8, "fear": 0.8,
    "restless": 0.7, "uneasy": 0.6, "tense": 0.7,
    "heart racing": 0.9, "can't breathe": 0.9,
    "panic attack": 1.0, "shaking": 0.8,
    "scared": 0.7, "afraid": 0.7, "paranoid": 0.8,
    "overwhelmed": 0.8, "pressure": 0.6,
    "social anxiety": 0.9, "performance anxiety": 0.8,
    "mind racing": 0.8, "can't relax": 0.7,
    "constant worry": 0.8, "feeling on edge": 0.8
}

HAPPY_KEYWORDS = {
    "happy": 0.8, "joyful": 0.9, "excited": 0.9, "grateful": 0.8,
    "blessed": 0.7, "content": 0.7, "peaceful": 0.7, "calm": 0.6,
    "relieved": 0.7, "hopeful": 0.7, "motivated": 0.7,
    "inspired": 0.8, "confident": 0.7, "proud": 0.8,
    "energized": 0.8, "cheerful": 0.8, "optimistic": 0.7,
    "thankful": 0.7, "loved": 0.8, "supported": 0.7,
    "accomplished": 0.8, "successful": 0.8, "thrilled": 0.9,
    "on top of the world": 1.0, "feeling good": 0.7,
    "life is good": 0.8, "everything is going well": 0.8,
    "things are improving": 0.7, "i feel amazing": 0.9,
    "i'm doing great": 0.8, "i feel strong": 0.7,
    "so grateful": 0.8, "very happy": 0.9,
    "super excited": 0.9, "overjoyed": 1.0,
    "feeling fantastic": 0.9, "this is wonderful": 0.8,
    "best day ever": 1.0, "dream come true": 1.0,
    "i love this": 0.7, "so proud of myself": 0.8,
    "feeling accomplished": 0.8
}

ANGRY_KEYWORDS = {
    "angry": 0.8, "furious": 1.0, "rage": 1.0, "mad": 0.7,
    "frustrated": 0.7, "irritated": 0.6, "annoyed": 0.5,
    "pissed": 0.8, "hate": 0.8, "disgusted": 0.7,
    "outraged": 0.9, "fed up": 0.7, "sick of": 0.7,
    "can't stand": 0.7, "drives me crazy": 0.7,
    "losing my temper": 0.8, "want to scream": 0.8,
    "so unfair": 0.6, "this is ridiculous": 0.6
}


def _calculate_weighted_score(text, keyword_dict):
    """Calculate a weighted emotion score based on keyword matches."""
    total_weight = 0.0
    match_count = 0
    for keyword, weight in keyword_dict.items():
        if keyword in text:
            total_weight += weight
            match_count += 1
    return total_weight, match_count


def detect_emotion(score, text):
    """
    Multi-stage emotion detection pipeline.
    
    Stage 1: Crisis keyword detection (highest priority)
    Stage 2: Greeting/farewell detection
    Stage 3: Weighted keyword analysis with confidence scoring
    Stage 4: VADER sentiment score fallback
    
    Returns: (emotion_label, confidence, details_dict)
    """
    if not text:
        return "neutral", 0.5, {"method": "empty_input"}

    text = text.lower().strip()

    # ─── Stage 1: Crisis Detection (Highest Priority) ───────────────────
    for keyword in CRISIS_KEYWORDS:
        if keyword in text:
            return "crisis", 1.0, {"method": "crisis_keyword", "matched": keyword}

    # ─── Stage 2: Greeting & Farewell Detection ─────────────────────────
    import re
    words_set = set(re.findall(r'\b\w+\b', text))
    text_clean = ' ' + text + ' '  # pad for multi-word matching

    for phrase in GREETINGS:
        if ' ' in phrase:
            # Multi-word: check as substring with word boundaries
            if phrase in text_clean:
                return "greeting", 0.9, {"method": "greeting_keyword"}
        else:
            # Single word: check in word set
            if phrase in words_set:
                return "greeting", 0.9, {"method": "greeting_keyword"}

    for phrase in FAREWELLS:
        if ' ' in phrase:
            if phrase in text_clean:
                return "farewell", 0.9, {"method": "farewell_keyword"}
        else:
            if phrase in words_set:
                return "farewell", 0.9, {"method": "farewell_keyword"}

    # ─── Stage 3: Weighted Keyword Analysis ─────────────────────────────
    deep_weight, deep_count = _calculate_weighted_score(text, DEEP_SAD_KEYWORDS)
    anx_weight, anx_count = _calculate_weighted_score(text, ANXIOUS_KEYWORDS)
    happy_weight, happy_count = _calculate_weighted_score(text, HAPPY_KEYWORDS)
    angry_weight, angry_count = _calculate_weighted_score(text, ANGRY_KEYWORDS)

    # Normalize weights to create confidence scores
    total_weight = deep_weight + anx_weight + happy_weight + angry_weight
    
    emotions = {
        "deep_sad": deep_weight,
        "anxious": anx_weight,
        "happy": happy_weight,
        "angry": angry_weight,
    }
    
    if total_weight > 0:
        # Find dominant emotion
        dominant = max(emotions, key=emotions.get)
        confidence = emotions[dominant] / max(total_weight, 1.0)
        
        # Build confidence scores for all emotions
        confidence_scores = {k: round(v / max(total_weight, 1.0), 2) for k, v in emotions.items()}

        if confidence >= KEYWORD_CONFIDENCE_MIN:
            # Special case: strong happiness → excited
            if dominant == "happy" and (happy_count >= 2 or happy_weight >= 1.5):
                return "excited", confidence, {
                    "method": "keyword_weighted",
                    "scores": confidence_scores,
                    "keyword_matches": happy_count
                }
            return dominant, confidence, {
                "method": "keyword_weighted",
                "scores": confidence_scores,
                "keyword_matches": emotions[dominant]
            }

    # ─── Stage 4: VADER Sentiment Fallback ──────────────────────────────
    details = {"method": "vader_sentiment", "compound_score": score}

    if score <= SENTIMENT_THRESHOLDS["deep_sad"]:
        return "deep_sad", abs(score), details
    elif score <= SENTIMENT_THRESHOLDS["mild_sad"]:
        return "mild_sad", abs(score), details
    elif score >= SENTIMENT_THRESHOLDS["excited"]:
        return "excited", score, details
    elif score >= SENTIMENT_THRESHOLDS["happy"]:
        return "happy", score, details
    else:
        return "neutral", 0.5, details


def detect_emotion_simple(score, text):
    """
    Backward-compatible wrapper that returns just the emotion label.
    Used by legacy code paths.
    """
    emotion, _, _ = detect_emotion(score, text)
    return emotion
