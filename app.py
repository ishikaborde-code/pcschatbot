from flask import Flask, render_template, request
import json
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

# ---- Load JSON knowledge base ----
with open("smart_ai_knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)["knowledge"]

# ---- Load embedding model ----
model = SentenceTransformer('all-MiniLM-L6-v2')

# ---- Precompute embeddings for all answers ----
for item in knowledge:
    item["embedding"] = model.encode(item["answer"], convert_to_tensor=True)

# ---- Chatbot logic ----
def chatbot_response(user_input):
    user_input = user_input.lower()

    # ---- EXIT / GOODBYE ----
    exit_words = ["bye", "goodbye", "exit", "quit", "stop"]
    for word in exit_words:
        if word in user_input:
            return "Goodbye! Have a great day ❤️"

    # ---- Semantic Matching ----
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    max_score = -1
    best_answer = ""

    for item in knowledge:
        score = util.cos_sim(user_embedding, item["embedding"]).item()
        if score > max_score:
            max_score = score
            best_answer = item["answer"]

    # ---- Irrelevant question handling (threshold) ----
    threshold = 0.5  # adjust based on testing
    if max_score < threshold:
        return "I can only answer questions about Artificial Intelligence. Try asking me something related to AI 🙂"

    return best_answer


# ---- Flask routes ----
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    return chatbot_response(user_text)


if __name__ == "__main__":
    app.run(debug=True)
