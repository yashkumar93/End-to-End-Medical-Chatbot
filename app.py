from flask import Flask, render_template, request, session
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from groq import Groq
from dotenv import load_dotenv
from src.prompt import system_prompt
from flask_cors import CORS
import os
import re
from uuid import uuid4

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
CORS(app, resources={r"/get": {"origins": os.environ.get("FRONTEND_URL", "*")}})

# Keeps recent chat turns per browser session in memory.
conversation_store = {}
MAX_HISTORY_MESSAGES = 12
SESSION_ID_KEY = "chat_session_id"

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PINECONE_HOST = os.environ.get("PINECONE_HOST")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "medicalbot")

if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in environment")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY in environment")

groq_client = Groq(api_key=GROQ_API_KEY)
embeddings = download_hugging_face_embeddings()

if PINECONE_HOST:
    cleaned_host = PINECONE_HOST.replace("https://", "").replace("http://", "").rstrip("/")
    docsearch = PineconeVectorStore(
        embedding=embeddings,
        pinecone_api_key=PINECONE_API_KEY,
        host=cleaned_host,
    )
else:
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
    )

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})


def sanitize_response(text: str) -> str:
    # Remove model reasoning blocks that should not be shown in the UI.
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"</?think>", "", text, flags=re.IGNORECASE)
    return text.strip()


def get_session_history():
    session_id = session.get(SESSION_ID_KEY)
    if not session_id:
        session_id = str(uuid4())
        session[SESSION_ID_KEY] = session_id

    history = conversation_store.setdefault(session_id, [])
    return history


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


@app.route("/get", methods=["GET", "POST"])
def chat():
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        msg = (payload.get("msg") or "").strip()
    else:
        msg = (request.form.get("msg") or "").strip()

    if not msg:
        return "Please enter a question.", 400

    history = get_session_history()

    docs = retriever.invoke(msg)
    context = "\n\n".join(doc.page_content for doc in docs)
    formatted_system_prompt = system_prompt.format(context=context)

    messages = [{"role": "system", "content": formatted_system_prompt}, *history, {"role": "user", "content": msg}]

    completion = groq_client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=messages,
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        reasoning_effort="default",
        stream=True,
    )

    response_text = ""
    for chunk in completion:
        response_text += chunk.choices[0].delta.content or ""

    cleaned_response = sanitize_response(response_text)

    history.extend([
        {"role": "user", "content": msg},
        {"role": "assistant", "content": cleaned_response},
    ])
    if len(history) > MAX_HISTORY_MESSAGES:
        del history[:-MAX_HISTORY_MESSAGES]

    return cleaned_response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
