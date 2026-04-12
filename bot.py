import os
import requests
from flask import Flask, request

TOKEN = "8381516564:AAHBCKfeR7wy3SQf6ntwsSUVAS1gsvZ1R0o"
GROQ = "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"
ADMIN = "8726418671"

app = Flask(__name__)

def ask(text, role=""):
    system = "Sen uzbek, rus va ingliz tillarida yordamchi botsan. Foydalanuvchi qaysi tilda yozsa shu tilda javob ber. " + role
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": "Bearer " + GROQ},
        json={"model": "llama-3.3-70b-versatile", "max_tokens": 2048,
              "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}]})
    return r.json()["choices"][0]["message"]["content"]

def send(chat_id, text, kb=None):
    data = {"chat_id": chat_id, "text": text}
    if kb:
        data["reply_markup"] = {"inline_keyboard": kb}
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=data)

def answer_cb(cb_id):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": cb_id})

@app.route("/", methods=["POST"])
def webhook():
    d = request.json

    if "callback_query" in d:
        cb = d["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        data = cb["data"]
        answer_cb(cb["id"])

        if data == "talaba":
            send(chat_id, "Talaba bolimi:", [[
                {"text": "Referat/Kurs ishi", "callback_data": "s_referat"},
                {"text": "Rezyume", "callback_data": "s_rezyume"}
            ],[
                {"text": "Intervyu", "callback_data": "s_intervyu"},
                {"text": "Ariza", "callback_data": "s_ariza"}
            ],[
                {"text": "Tarjima", "callback_data": "s_tarjima"}
            ],[
                {"text": "Bosh menyu", "callback_data": "start"}
            ]])
        elif data == "oquvchi":
            send(chat_id, "Oquvchi bolimi:", [[
                {"text": "Texnologik karta", "callback_data": "s_texkarta"},
                {"text": "Test yaratish", "callback_data": "s_test"}
            ],[
                {"text": "Dars rejasi", "callback_data": "s_darsreja"},
                {"text": "Ota-onalarga xat", "callback_data": "s_xat"}
            ],[
                {"text": "Tavsifnoma", "callback_data": "s_tavsif"},
                {"text": "Tarjima", "callback_data": "s_tarjima"}
            ],[
                {"text": "Bosh menyu", "callback_data": "start"}
            ]])
        elif data == "ofis":
            send(chat_id, "Ofis xodimi bolimi:", [[
                {"text": "Reklama matni", "callback_data": "s_reklama"},
                {"text": "Biznes-reja", "callback_data": "s_biznes"}
            ],[
                {"text": "Mahsulot tavsifi", "callback_data": "s_mahsulot"},
                {"text": "Email/Xat", "callback_data": "s_email"}
            ],[
                {"text": "Ariza", "callback_data": "s_ariza"},
                {"text": "Tarjima", "callback_data": "s_tarjima"}
            ],[
                {"text": "Bosh menyu", "callback_data": "start"}
            ]])
        elif data == "start":
            send(chat_id, "Siz kimSiz?", [[
                {"text": "Talaba", "callback_data": "talaba"}
            ],[
                {"text": "Oquvchi", "callback_data": "oquvchi"}
            ],[
                {"text": "Ofis xodimi", "callback_data": "ofis"}
            ]])
        elif data.startswith("s_"):
            xizmat = data[2:]
            savollar = {
                "referat": "Referat mavzusini yozing:",
                "rezyume": "Tajriba va konnikmalaringizni yozing:",
                "intervyu": "Qaysi lavozimga intervyu?",
                "ariza": "Ariza kimga va nima uchun?",
                "tarjima": "Matnni yozing (qaysi tildan qaysi tilga):",
                "texkarta": "Dars mavzusi va sinfni yozing:",
                "test": "Mavzu va nechta savol kerak?",
                "darsreja": "Dars mavzusi va sinfni yozing:",
                "xat": "Xat mavzusini yozing:",
                "tavsif": "Oquvchi ismi va sababini yozing:",
                "reklama": "Mahsulot yoki xizmat haqida yozing:",
                "biznes": "Biznes goyangizni yozing:",
                "mahsulot": "Mahsulotingiz haqida yozing:",
                "email": "Kimga va nima haqida?"
            }
            if xizmat in savollar:
                send(chat_id, savollar[xizmat], [[
                    {"text": "Bosh menyu", "callback_data": "start"}
                ]])
        return "ok"

    if "message" not in d:
        return "ok"

    chat_id = d["message"]["chat"]["id"]
    text = d["message"].get("text", "")

    if text == "/start":
        send(chat_id, "Salom! Siz kimSiz?", [[
            {"text": "Talaba", "callback_data": "talaba"}
        ],[
            {"text": "Oquvchi", "callback_data": "oquvchi"}
        ],[
            {"text": "Ofis xodimi", "callback_data": "ofis"}
        ]])
    elif text.startswith("/reklama ") and str(chat_id) == ADMIN:
        msg = text[9:]
        send(chat_id, "Reklama yuborilmoqda...")
    else:
        send(chat_id, "Tayyorlanmoqda...")
        javob = ask(text)
        send(chat_id, javob, [[
            {"text": "Bosh menyu", "callback_data": "start"}
        ]])

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
