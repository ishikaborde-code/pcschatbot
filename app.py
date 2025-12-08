from flask import Flask, render_template, request, jsonify
import json
import random
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import re

app = Flask(__name__)

# ---- Load JSON Knowledge Base ----
with open("ai_knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)["knowledge"]

knowledge_texts = [item["text"] for item in knowledge]

# ---- Create Embeddings ----
embedding_model_name = "all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(embedding_model_name)
knowledge_embeddings = embedding_model.encode(knowledge_texts, convert_to_tensor=False)

# ---- FAISS Index for Semantic Search ----
dimension = knowledge_embeddings[0].shape[0]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(knowledge_embeddings).astype("float32"))

# ---- Dynamic Self-Generative Response ----
AI_KEYWORDS = ["AI", "artificial", "intelligence", "machine", "learning", "model",
               "algorithm", "data", "automation", "reasoning", "technology", "knowledge"]

def is_ai_related(user_input):
    # Check if user input contains any AI-related keywords
    return any(word.lower() in user_input.lower() for word in AI_KEYWORDS)

def generate_dynamic_response(user_input, sentences=2):
    # Keywords fallback
    keywords = ["AI", "learning", "model", "data", "reasoning", "algorithm",
                "knowledge", "automation", "future", "intelligence", "technology"]

    # Extract meaningful words from user input
    user_words = [w for w in re.findall(r'\w+', user_input) if len(w) > 3]

    # Mix of keywords from input or fallback
    if user_words:
        words = random.sample(user_words, min(len(user_words), 3))
    else:
        words = random.sample(keywords, 2)

    # Templates for dynamic sentences
    templates = [
        "{} plays an important role in understanding AI concepts.",
        "When we consider {}, it helps us improve models and decision-making.",
        "Exploring {} can provide new insights into technology and data.",
        "In the context of AI, {} often contributes to better learning and reasoning.",
        "Understanding {} is crucial for advancing knowledge in this field.",
        "Considering {}, one can see its impact on automation and future applications.",
        "Examining {} can enhance our perspective on AI and related tasks."
    ]

    # Generate multiple sentences
    response_sentences = []
    for i in range(sentences):
        word = random.choice(words)
        sentence = random.choice(templates).format(word)
        response_sentences.append(sentence)

    response = " ".join(response_sentences)
    return response

# ---- Chatbot Logic ----
previous_answers = []

def chatbot_response(user_input):
    global previous_answers

    # Encode user input
    user_embedding = embedding_model.encode(user_input, convert_to_tensor=False)

    # Search FAISS index
    D, I = index.search(np.array([user_embedding]).astype("float32"), k=1)
    best_index = I[0][0]
    best_score = D[0][0]

    similarity_threshold = 1.0

    if best_score < similarity_threshold:
        # Relevant -> combine JSON + dynamic
        knowledge_answer = knowledge_texts[best_index]
        dynamic_answer = generate_dynamic_response(user_input, sentences=2)
        response = f"{knowledge_answer}. {dynamic_answer}"
    else:
        # Low similarity -> check if AI-related
        if is_ai_related(user_input):
            response = generate_dynamic_response(user_input, sentences=2)
        else:
            response = "Sorry, this is outside my knowledge/context."

    # Avoid repetition
    attempt = 0
    while response in previous_answers and attempt < 5:
        if is_ai_related(user_input):
            response = generate_dynamic_response(user_input, sentences=2)
        else:
            response = "Sorry, this is outside my knowledge/context."
        attempt += 1

    previous_answers.append(response)

    if len(previous_answers) > 20:
        previous_answers.pop(0)

    # Clean output
    response = response.replace("\n", " ").replace("\\n", " ")
    return response

# ---- Flask Routes ----
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["GET", "POST"])
def get_response():
    try:
        user_input = request.form.get("msg") or request.args.get("msg")
        if not user_input:
            return jsonify({"response": "Please type something!"})
        bot_reply = chatbot_response(user_input)
        return jsonify({"response": bot_reply})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

# ---- Run App ----
if __name__ == "__main__":
    app.run(debug=True)
