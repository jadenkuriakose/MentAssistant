import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_executor import Executor
from groq import Groq
from textblob import TextBlob  
import re

load_dotenv()

app = Flask(__name__)
CORS(app)
executor = Executor(app)

sessions = {}

def analyze_input_length(prompt):
    input_length = len(prompt.split())
    if input_length < 20:
        return 50
    elif input_length < 50:
        return 150
    else:
        return 300

def analyze_sentiment_and_risk(prompt):
    sentiment = TextBlob(prompt).sentiment
    polarity = sentiment.polarity
    subjectivity = sentiment.subjectivity
    risk_score = 0

    if polarity < 0:
        risk_score = 0.7  # High risk if sentiment is negative
    elif polarity > 0:
        risk_score = 0.3  # Low risk if sentiment is positive
    else:
        risk_score = 0.5  # Medium risk for neutral sentiment

    return polarity, subjectivity, risk_score

def generate_response(prompt, session_id):
    api_key = os.getenv("API_KEY")
    if not api_key:
        return "API key not found.", 500

    client = Groq(api_key=api_key)

    try:
        messages = sessions.get(session_id, [])
        messages.append({"role": "user", "content": prompt})

        max_tokens = analyze_input_length(prompt)

        sentiment_polarity, sentiment_subjectivity, risk_score = analyze_sentiment_and_risk(prompt)

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
            top_p=0.9,
            stream=True,
            stop=None,
        )

        bot_response = "".join(
            chunk.choices[0].delta.content or "" for chunk in completion
        ).strip()

        messages.append({"role": "assistant", "content": bot_response})
        sessions[session_id] = messages

        return {
            "response": bot_response,
            "sentiment": {
                "polarity": sentiment_polarity,
                "subjectivity": sentiment_subjectivity,
            },
            "risk_score": risk_score,
        }, 200

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
        return jsonify(response), 200
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


