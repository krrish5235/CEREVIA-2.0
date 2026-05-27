import json
import random
def generate_response(emotion):
    with open("ai_chatbot/templates.json", "r") as f:
        templates = json.load(f)
    
    if emotion not in templates:
        emotion = "random"
    
    responses = templates.get(emotion, templates["neutral"])
    return random.choice(responses)