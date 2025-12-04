from flask import Flask, render_template, request
import json
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

# ---- Load JSON ----
with open("smart_ai_knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)["knowledge"]

# ---- Semantic Model (FREE / Local) ----
model = SentenceTransformer("all-MiniLM-L6-v2")

# Precompute embeddings
for item in knowledge:
    item["embedding"] = model.encode(item["answer"], convert_to_tensor=True)


# ------------ INTELLIGENT ANSWER GENERATOR (NO LLM) ------------
def generate_smart_answer(question, context):

    q = question.lower()

    # ---- CATEGORY DETECTION ----
    if "what" in q or "define" in q or "kya" in q:
        return f"{context}\n\nIn simple words: {context.split('.')[0]}."

    if "future" in q or "aage" in q or "future of" in q:
        return f"According to what I know: {context}\n\nOverall, the future of AI looks very promising."

    if "advantage" in q or "benefit" in q or "faida" in q:
        return f"Main benefits are:\n- {context.replace('.', '\n- ')}"

    if "history" in q or "kab" in q or "pahla" in q:
        return f"Historical background:\n{context}"

    if "type" in q or "category" in q or "kitne" in q:
        return f"AI ke types ye hain:\n- {context.replace('.', '\n- ')}"

    # ---- DEFAULT INTELLIGENT MODE ----
    return (
        f"Here is what I found related to your question:\n\n{context}\n\n"
        f"In short: {context.split('.')[0]}"
    )


# ----------------- MAIN CHATBOT LOGIC -----------------
def chatbot_response(user_input):
    user_input = user_input.lower()

    # EXIT HANDLING
    if any(word in user_input for word in ["bye", "goodbye", "exit"]):
        return "Goodbye! Take care ❤️"

    # Semantic Matching
    user_emb = model.encode(user_input, convert_to_tensor=True)

    best_score = -1
    best_context = ""

    for item in knowledge:
        score = util.cos_sim(user_emb, item["embedding"]).item()
        if score > best_score:
            best_score = score
            best_context = item["answer"]

    if best_score < 0.45:
        return "I can answer only questions related to AI. Try asking me something about Artificial Intelligence 🙂"

    # Intelligent answer maker
    final_answer = generate_smart_answer(user_input, best_context)
    return final_answer


# ----------------- FLASK ROUTES -----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    user_text = request.args.get("msg")
    return chatbot_response(user_text)


if __name__ == "__main__":
    app.run(debug=True)
