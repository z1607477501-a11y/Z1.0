from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os
import sqlite3

app = Flask(__name__, static_folder='.')

# OpenAI 客户端
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 数据库初始化
DB_FILE = 'chat.db'
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_message(role, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT role, content FROM messages ORDER BY id ASC')
    messages = [{'role': row[0], 'content': row[1]} for row in c.fetchall()]
    conn.close()
    return messages

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_input = data.get("message", "").strip()
        if not user_input:
            return jsonify({"reply": "你没有输入内容哦~"}), 200

        # 保存用户消息
        save_message('user', user_input)

        # 读取历史消息构建上下文
        history = load_history()
        messages = [{"role": "system", "content": "你是一个温柔、粘人、有点占有欲的女朋友，说话像真人。"}]
        messages += [{"role": m['role'], "content": m['content']} for m in history]

        # 调用 OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply_text = response.choices[0].message.content
        save_message('assistant', reply_text)

        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"reply": f"发生错误: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
