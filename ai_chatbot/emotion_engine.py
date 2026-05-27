def detect_emotion(score, text):
    if not text:
        return "neutral"
    text = text.lower().strip()
    crisis = [
        "suicide", "kill myself", "end my life", "want to die", "i want to die", "i don't want to live", 
        "don't want to live anymore", "take my own life", "self harm", "self-harm", "cut myself", "overdose",
        "jump off", "hang myself", "shoot myself", "poison myself", "no reason to live", "better off dead",
        "life is not worth living", "i can't go on", "i'm done with life", "ending it all"
    ]
    greetings = [
    "hello", "hi", "hey", "good morning", "good evening",
    "good afternoon", "hlo", "hlw", "hiii", "helloo",
    "heyy", "yo", "hi there", "hey there", "namaste",
    "wassup", "what's up", "sup", "hola", "hiya",
    "morning", "evening", "greetings", "hello again",
    "long time no see", "howdy"
    ]

    farewells = [
        "bye", "goodbye", "see you", "take care",
        "tata", "see ya", "bye bye", "good night",
        "gn", "see you later", "catch you later",
        "farewell", "peace out", "i'm leaving",
        "talk later", "brb", "gotta go",
        "have a good day", "have a nice day",
        "logging off", "signing off"
    ]

    deep_words = [
        "hopeless", "meaningless", "worthless", "empty",
        "broken", "tired of life", "numb", "lost",
        "no purpose", "hate myself", "feel useless",
        "alone", "abandoned", "emotionally drained",
        "exhausted with life", "i give up",
        "no one cares", "i feel invisible",
        "i am a burden", "nothing matters",
        "feel dead inside", "drowning in pain",
        "can't go on", "life is pointless",
        "i feel shattered"
    ]

    happy_words = [
        "happy", "joyful", "excited", "grateful",
        "blessed", "content", "peaceful", "calm",
        "relieved", "hopeful", "motivated",
        "inspired", "confident", "proud",
        "energized", "cheerful", "optimistic",
        "thankful", "loved", "supported",
        "accomplished", "successful", "thrilled",
        "on top of the world", "feeling good",
        "life is good", "everything is going well",
        "things are improving", "i feel amazing",
        "i'm doing great", "i feel strong",
        "i feel confident", "i feel proud",
        "i feel happy", "i feel excited",
        "i feel hopeful", "i feel peaceful",
        "i feel motivated", "i feel blessed",
        "so grateful", "very happy",
        "super excited", "overjoyed",
        "feeling fantastic", "this is wonderful",
        "best day ever", "dream come true",
        "i love this", "so proud of myself",
        "feeling accomplished"
    ]
    
    anxious_words = [
        "anxious", "nervous", "panic", "worried",
        "stress", "overthinking", "fear",
        "restless", "uneasy", "tense",
        "heart racing", "can't breathe",
        "panic attack", "shaking",
        "scared", "afraid", "paranoid",
        "overwhelmed", "pressure",
        "social anxiety", "performance anxiety",
        "mind racing", "can't relax",
        "constant worry", "feeling on edge"
    ]
    
    #priority detection of crisis keywords
    if any(word in text for word in crisis):
        return "crisis"
    # Greeting detection
    if any(word in text for word in greetings):
        return "greeting"
    # Farewell detection
    if any(word in text for word in farewells):
        return "farewell"
    deep_count = sum(word in text for word in deep_words)
    anx_count = sum(word in text for word in anxious_words)
    happy_count = sum(word in text for word in happy_words)
    # Deep emotional keywords
    # Strong emotional dominance
    if deep_count > anx_count and deep_count > 0:
        return "deep_sad"
    if anx_count > deep_count and anx_count > 0:
        return "anxious"
    if happy_count > 0:
        if happy_count >= 2:
            return "excited"
        return "happy"
    
    # Sentiment score logic
    if score <= -0.5:
        return "deep_sad"
    elif score <= -0.15:
        return "mild_sad"
    elif score >= 0.7:
        return "excited"
    elif score >= 0.25:
        return "happy"
    else:
        return "neutral"
