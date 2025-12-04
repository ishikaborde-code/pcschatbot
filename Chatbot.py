# chatbot_basic.py
import json

# ----------------- Load JSON Knowledge -----------------
with open("ai_knowledge.json", "r", encoding="utf-8") as f:
    data = json.load(f)

knowledge = data["knowledge"]

# ----------------- Simple String Matching Function -----------------
def chatbot_response(user_input):
    user_input = user_input.lower()
    max_match = 0
    best_response = ""

    for sentence in knowledge:
        sentence_lower = sentence.lower()
        # Count number of common words
        common_words = set(user_input.split()) & set(sentence_lower.split())
        match_score = len(common_words)

        if match_score > max_match:
            max_match = match_score
            best_response = sentence

    # If no match or too low match
    if max_match == 0:
        return "Hmm… that’s interesting! But I’m only trained to talk about Artificial Intelligence. Try asking me about AI"
    else:
        return best_response

# ----------------- Chat Loop -----------------
print("AI Chatbot (Pure Python) ready! Type 'exit' to quit.")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    response = chatbot_response(user_input)
    print("Bot:", response)
