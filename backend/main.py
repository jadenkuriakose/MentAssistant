import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_executor import Executor
from groq import Groq

load_dotenv()

app = Flask(__name__)
CORS(app)
executor = Executor(app)

sessions = {}

def generate_response(prompt, session_id):
    api_key = os.getenv("API_KEY")
    if not api_key:
        return "API key not found.", 500

    client = Groq(api_key=api_key)

    try:
        messages = sessions.get(session_id, [])
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9,
            stream=True,
            stop=None,
        )

        bot_response = "".join(
            chunk.choices[0].delta.content or "" for chunk in completion
        ).strip()

        messages.append({"role": "assistant", "content": bot_response})
        sessions[session_id] = messages

        return bot_response, 200

    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    session_id = data.get("session_id", "").strip()

    if not prompt or not session_id:
        return jsonify({"error": "Prompt and session ID are required."}), 400

    if session_id not in sessions:
        sessions[session_id] = []

    response, status_code = generate_response(prompt, session_id)
    if status_code == 200:
        return jsonify({"response": response}), 200
    else:
        return jsonify({"error": response}), status_code

@app.route("/end_session", methods=["POST"])
def end_session():
    data = request.get_json()
    session_id = data.get("session_id", "").strip()

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid or missing session ID."}), 400

    del sessions[session_id]
    return jsonify({"message": "Session ended."}), 200

if __name__ == "__main__":
    app.run(debug=True, port=8080)
