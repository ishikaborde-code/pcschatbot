from flask import Flask, render_template, request
import json

app = Flask(__name__)

# Load JSON knowledge base
with open("ai_knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)["knowledge"]

# Chatbot logic
def chatbot_response(user_input):
    user_input = user_input.lower()

    # ---- EXIT / GOODBYE CONDITION ----
    exit_words = ["bye", "goodbye", "exit", "quit", "stop"]
    for word in exit_words:
        if word in user_input:
            return "Goodbye! Have a great day ❤️"

    # ---- AI Keyword Matching ----
    max_match = 0
    best_answer = ""

    for item in knowledge:
        for keyword in item["question"]:
            keyword = keyword.lower()

            common_words = set(user_input.split()) & set(keyword.split())
            match_score = len(common_words)

            if match_score > max_match:
                max_match = match_score
                best_answer = item["answer"]

    # If nothing matched
    if max_match == 0:
        return "I can only answer questions about Artificial Intelligence. Try asking me anything related to AI 🙂"

    return best_answer


# Flask routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    return chatbot_response(user_text)

if __name__ == "__main__":
    app.run(debug=True)
