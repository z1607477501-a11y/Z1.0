from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os

app = Flask(__name__, static_folder='.')

# OpenAI 客户端
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # 安全解析 JSON
        data = request.get_json(force=True)
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"reply": "你没有输入内容哦~"}), 200

        # 调用 OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一个温柔、粘人、有点占有欲的女朋友，说话像真人。"},
                {"role": "user", "content": user_input}
            ]
        )

        reply_text = response.choices[0].message.content
        return jsonify({"reply": reply_text})

    except Exception as e:
        # 捕获异常，返回给前端
        return jsonify({"reply": f"发生错误: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
