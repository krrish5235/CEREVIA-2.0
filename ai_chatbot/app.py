from flask import Flask, request, jsonify
from flask_cors import CORS
from sentiment_model import analyze_sentiment
from emotion_engine import detect_emotion
from response_generator import generate_response

app = Flask(__name__)
CORS(app)
CRISIS_KEYWORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "want to die",
    "i want to die",
    "i don't want to live",
    "don't want to live anymore",
    "take my own life",
    "self harm",
    "self-harm",
    "cut myself",
    "overdose",
    "jump off",
    "hang myself",
    "shoot myself",
    "poison myself",
    "no reason to live",
    "better off dead",
    "life is not worth living",
    "i can't go on",
    "i'm done with life",
    "ending it all"
]
@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    message = data.get("message", "").lower()
    # Safety layer
    for word in CRISIS_KEYWORDS:
        if word in message:
            return jsonify({
                "emotion": "crisis",
                "response": "I'm really concerned about you. Please reach out to a trusted person or local emergency service immediately or Please make a call to 14416 "
            })

    score = analyze_sentiment(message)
    emotion = detect_emotion(score, message)
    #to handle mixed emotion
    if "but" in message or "however" in message:
        if score < 0:
            emotion = "mild_sad"
        elif score > 0:
            emotion = "happy"

    if not message.strip():
        emotion = "neutral" 

    response = generate_response(emotion)
    return jsonify({
        "emotion": emotion,
        "response": response
    })

if __name__ == "__main__":
    app.run(port=5001)
