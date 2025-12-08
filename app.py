from flask import Flask, render_template, request, jsonify
import json
import random
import re

# LangChain imports
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings

app = Flask(__name__)

# ---- Load JSON Knowledge Base ----
with open("ai_knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)["knowledge"]

knowledge_texts = [item["text"] for item in knowledge]

# ---- LangChain Embeddings and FAISS Vector Store ----
embedding_model_name = "all-MiniLM-L6-v2"
embeddings = SentenceTransformerEmbeddings(model_name=embedding_model_name)
vector_store = FAISS.from_texts(knowledge_texts, embeddings)

# ---- Goodbye Detection ----
def is_goodbye(user_input):
    goodbye_words = [
        "bye", "byee","exit", "goodbye", "bye bye", "bbye", 
        "tata", "see you", "see ya", "good night","quit"
    ]
    user_input = user_input.lower()
    return any(word in user_input for word in goodbye_words)

# ---- AI Keywords for Context Check ----
AI_KEYWORDS = ["ai", "artificial", "intelligence", "machine", "learning", "model",
               "algorithm", "data", "automation", "reasoning", "technology", "knowledge"]

def is_ai_related(user_input):
    return any(word in user_input.lower() for word in AI_KEYWORDS)

# ---- Dynamic Self-Generative Response ----
def generate_dynamic_response(user_input, sentences=2):
    keywords = ["AI", "learning", "model", "data", "reasoning", "algorithm",
                "knowledge", "automation", "future", "intelligence", "technology"]
    user_words = [w for w in re.findall(r'\w+', user_input) if len(w) > 3]
    words = random.sample(user_words, min(len(user_words), 3)) if user_words else random.sample(keywords, 2)

    templates = [
        "{} plays an important role in understanding AI concepts.",
        "When we consider {}, it helps us improve models and decision-making.",
        "Exploring {} can provide new insights into technology and data.",
        "In the context of AI, {} often contributes to better learning and reasoning.",
        "Understanding {} is crucial for advancing knowledge in this field.",
        "Considering {}, one can see its impact on automation and future applications.",
        "Examining {} can enhance our perspective on AI and related tasks."
    ]

    response_sentences = [random.choice(templates).format(random.choice(words)) for _ in range(sentences)]
    response = " ".join(response_sentences)
    
    response = response.replace("\n", " ").replace("\\n", " ")
    response = " ".join(response.split())
    return response

# ---- Chatbot Logic ----
previous_answers = []

def chatbot_response(user_input):
    global previous_answers

    # ---- Check for GOODBYE ----
    if is_goodbye(user_input):
        return "Good bye! Take care 😊"

    # ---- Search in FAISS Vector Store ----
    docs_and_scores = vector_store.similarity_search_with_score(user_input, k=1)
    if docs_and_scores:
        best_doc, score = docs_and_scores[0]
    else:
        best_doc, score = None, None

    similarity_threshold = 1.0

    if best_doc and score < similarity_threshold:
        knowledge_answer = best_doc.page_content
        dynamic_answer = generate_dynamic_response(user_input, sentences=2)
        response = f"{knowledge_answer}. {dynamic_answer}"
    else:
        if is_ai_related(user_input):
            response = generate_dynamic_response(user_input, sentences=2)
        else:
            response = "Sorry, this is outside my knowledge/context."

    # ---- Avoid Repeating Same Response ----
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

    # ---- Clean Output ----
    response = response.replace("\n", " ").replace("\\n", " ")
    response = " ".join(response.split())

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

        # ⭐ IMPORTANT FIX — NO MORE \ud83d\ude0a
        return app.response_class(
            response=json.dumps({"response": bot_reply}, ensure_ascii=False),
            mimetype="application/json"
        )

    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

# ---- Run Flask App ----
if __name__ == "__main__":
    app.run(debug=True)
