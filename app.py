
# from flask import Flask, render_template, request
# import json
# from sentence_transformers import SentenceTransformer, util
# from collections import deque
# from langdetect import detect

# app = Flask(__name__)

# # ---- Load JSON (chunked text) ----
# with open("ai_knowledge.json", "r", encoding="utf-8") as f:
#     knowledge = json.load(f)["knowledge"]

# # ---- Semantic Model ----
# model = SentenceTransformer("all-MiniLM-L6-v2")

# # Memory (last 3 messages)
# memory = deque(maxlen=3)

# # ---------- PRECOMPUTE EMBEDDINGS ----------
# for item in knowledge:
#     text = item.get("text", "")
#     item["embedding"] = model.encode(text, convert_to_tensor=True)

# # ---------- SIMPLE HINDI → ENGLISH TRANSLATOR ----------
# def translate_to_english(text):
#     hindi_to_eng = {
#         "kya": "what",
#         "kaise": "how",
#         "kyu": "why",
#         "kab": "when",
#         "kaun": "who",
#         "kaha": "where",
#         "faida": "benefit",
#         "nuksan": "disadvantage",
#         "aage": "future",
#         "samjhao": "explain",
#         "batao": "tell",
#         "aur": "more",
#     }
#     words = text.split()
#     translated = [hindi_to_eng.get(w.lower(), w) for w in words]
#     return " ".join(translated)

# # ---------- SMART ANSWER MAKER ----------
# def generate_smart_answer(question, context, memory_used=False):
#     q = question.lower()

#     # Follow-up question
#     if any(word in q for word in ["more", "continue", "explain more"]):
#         return (
#             "Sure! Based on our previous discussion:\n"
#             f"{memory[-1] if memory else context}\n\n"
#             f"Additional explanation:\n{context}"
#         )

#     # Category logic
#     if "what" in q or "define" in q:
#         return f"{context}\n\nIn simple words: {context.split('.')[0]}"

#     if "future" in q:
#         return f"Here is what I found about the future:\n{context}\n\nIn short: The future of AI looks very promising."

#     if "benefit" in q or "advantage" in q:
#         return "Here are the advantages:\n- " + context.replace(".", "\n- ")

#     if "history" in q or "when" in q or "first" in q:
#         return f"Historical information:\n{context}"

#     if "type" in q or "category" in q:
#         return "Types include:\n- " + context.replace(".", "\n- ")

#     tone = "Let me explain clearly:" if memory_used else "Here’s what I found:"
#     return f"{tone}\n{context}\n\nShort summary: {context.split('.')[0]}"

# # ---------- MAIN CHATBOT LOGIC ----------
# def chatbot_response(user_input):

#     # Auto translate Hindi → English
#     try:
#         if detect(user_input) != "en":
#             user_input = translate_to_english(user_input)
#     except:
#         pass

#     user_input = user_input.lower()

#     # Exit condition
#     if any(word in user_input for word in ["bye", "goodbye", "exit"]):
#         return "Goodbye! Take care ❤️"

#     # Add to memory
#     memory.append(user_input)

#     # Semantic matching
#     user_emb = model.encode(user_input, convert_to_tensor=True)

#     best_score = -1
#     best_context = ""
#     memory_used = False

#     for item in knowledge:
#         score = util.cos_sim(user_emb, item["embedding"]).item()
#         if score > best_score:
#             best_score = score
#             best_context = item["text"]

#     # Weak match case
#     if best_score < 0.40:
#         if len(memory) >= 2:
#             memory_used = True
#             return generate_smart_answer(user_input, memory[-2], memory_used=True)
#         return (
#             "I can answer only questions related to Artificial Intelligence. "
#             "Please ask me something about AI 🙂"
#         )

#     # Strong match → smart answer
#     final_answer = generate_smart_answer(user_input, best_context, memory_used=False)
#     return final_answer

# # ---------- FLASK ROUTES ----------
# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/get")
# def get_bot_response():
#     user_text = request.args.get("msg")
#     return chatbot_response(user_text)

# if __name__ == "__main__":
#     app.run(debug=True)
from flask import Flask, render_template, request
import json
from sentence_transformers import SentenceTransformer, util
from collections import deque
from langdetect import detect

app = Flask(__name__)

# ----------------------------------------------------
# LOAD KNOWLEDGE BASE
# ----------------------------------------------------
with open("ai_knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)["knowledge"]

# ----------------------------------------------------
# LOAD SEMANTIC MODEL
# ----------------------------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# Memory (last 3 messages)
memory = deque(maxlen=3)

# ----------------------------------------------------
# PRECOMPUTE EMBEDDINGS
# ----------------------------------------------------
for item in knowledge:
    text = item.get("text", "")
    item["embedding"] = model.encode(text, convert_to_tensor=True)


# ----------------------------------------------------
# SIMPLE HINDI → ENGLISH TRANSLATION
# ----------------------------------------------------
def translate_to_english(text):
    mapping = {
        "kya": "what",
        "ky": "what",
        "kaise": "how",
        "kyu": "why",
        "kab": "when",
        "kaun": "who",
        "kaha": "where",
        "faida": "benefit",
        "nuksan": "disadvantage",
        "aage": "future",
        "samjhao": "explain",
        "samjha": "explain",
        "batao": "tell",
        "bataye": "tell",
        "aur": "more",
        "history": "history",
        "itihaas": "history",
        "type": "type",
    }

    words = text.split()
    translated = [mapping.get(w.lower(), w) for w in words]
    return " ".join(translated)


# ----------------------------------------------------
# SMART ANSWER MAKER
# ----------------------------------------------------
def generate_smart_answer(question, context, memory_used=False):

    q = question.lower()

    if any(w in q for w in ["more", "continue", "explain more"]):
        if memory:
            return (
                f"Based on previous discussion:\n{memory[-1]}\n\n"
                f"More details:\n{context}"
            )
        return context

    if "what" in q or "define" in q:
        return f"{context}\n\nIn simple words: {context.split('.')[0]}."

    if "future" in q:
        return f"Future of AI:\n{context}\n\nShort summary: AI is growing fast."

    if "benefit" in q or "advantage" in q:
        pts = context.replace(".", "\n- ")
        return "Advantages:\n- " + pts

    if "history" in q or "when" in q or "first" in q:
        return f"History:\n{context}"

    if "type" in q or "category" in q:
        return "Types:\n- " + context.replace(".", "\n- ")

    tone = "Let me explain:" if memory_used else "Here’s what I found:"
    return f"{tone}\n{context}\n\nSummary: {context.split('.')[0]}."


# ----------------------------------------------------
# MAIN CHATBOT LOGIC
# ----------------------------------------------------
def chatbot_response(user_input):

    # Language detection
    try:
        if detect(user_input) != "en":
            user_input = translate_to_english(user_input)
    except:
        pass

    user_input = user_input.lower()

    # Exit
    if any(w in user_input for w in ["bye", "goodbye", "exit"]):
        return "Goodbye! Take care ❤️"

    # Memory update
    memory.append(user_input)

    # --------------------------------------------------------
    # JSON WORD-LEVEL MATCH SYSTEM (STRICT FILTER)
    # --------------------------------------------------------
    json_words = set()
    for item in knowledge:
        for w in item["text"].lower().split():
            json_words.add(w)

    user_words = set(user_input.split())

    # If NO word matched → NO ANSWER
    if len(json_words.intersection(user_words)) == 0:
        return (
            "I can answer only questions related to Artificial Intelligence. "
            "Please ask something from the AI knowledge base 🙂"
        )

    # --------------------------------------------------------
    # SEMANTIC MATCH (ONLY IF TEXT MATCHES)
    # --------------------------------------------------------
    user_emb = model.encode(user_input, convert_to_tensor=True)

    best_score = -1
    best_context = ""

    for item in knowledge:
        score = util.cos_sim(user_emb, item["embedding"]).item()
        if score > best_score:
            best_score = score
            best_context = item["text"]

    # Weak score → even though words matched, refuse to answer
    if best_score < 0.40:
        return (
            "I can answer only questions related to Artificial Intelligence. "
            "Please ask something relevant to AI 🙂"
        )

    # Strong match → final answer
    return generate_smart_answer(user_input, best_context)


# ----------------------------------------------------
# FLASK ROUTES
# ----------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    user_text = request.args.get("msg")
    return chatbot_response(user_text)


if __name__ == "__main__":
    app.run(debug=True)
