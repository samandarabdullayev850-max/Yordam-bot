import os
import requests
from flask import Flask, request

TOKEN = "8381516564:AAHBCKfeR7wy3SQf6ntwsSUVAS1gsvZ1R0o"
GROQ = "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"

app = Flask(__name__)

def ask(text):
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": "Bearer " + GROQ},
        json={"model": "llama-3.3-70b-versatile", "max_tokens": 1024,
              "messages": [{"role": "system", "content": "Sen uzbek, rus va ingliz tillarida yordamchi botsan. Foydalanuvchi qaysi tilda yozsa shu tilda javob ber."}, {"role": "user", "content": text}]})
    return r.json()["choices"][0]["message"]["content"]

def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text})

@app.route("/", methods=["POST"])
def webhook():
    d = request.json
    if "message" in d:
        chat_id = d["message"]["chat"]["id"]
        text = d["message"].get("text", "")
        if text == "/start":
            send(chat_id, "Salom! Men sizning aqlli yordamchingizman. Savol bering!")
        else:
            send(chat_id, ask(text))
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
