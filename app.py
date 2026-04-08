from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os

app = Flask(__name__, static_folder='.')

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一个温柔、粘人、有点占有欲的女朋友，说话像真人。"},
            {"role": "user", "content": user_input}
        ]
    )

    return jsonify({"reply": response.choices[0].message.content})

if __name__ == "__main__":
   import os
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
