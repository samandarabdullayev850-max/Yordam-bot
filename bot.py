import os
import requests
from flask import Flask, request
from datetime import datetime

SHEETS_URL = "https://script.google.com/macros/s/AKfycbzRnJbIKgsjpTb8SfNv6nJ4yfzmVoyEg4pdVpQhzqavsx6bNNYrws84FXFB7bEbNEcc1g/exec"
TOKEN = "8381516564:AAHBCKfeR7wy3SQf6ntwsSUVAS1gsvZ1R0o"
GROQ = "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"
ADMIN = "8726418671"
CHANNEL = "@sizning_kanal"
OBUNA_MAJBURIY = False

app = Flask(name)

def save_user(user_id, ism, bulim="", xizmat=""):
    try:
        requests.post(SHEETS_URL, json={
            "user_id": str(user_id),
            "ism": ism,
            "sana": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "bulim": bulim,
            "xizmat": xizmat
        })
    except:
        pass

def ask(text, role=""):
    system = "Sen uzbek, rus va ingliz tillarida yordamchi botsan. Foydalanuvchi qaysi tilda yozsa shu tilda javob ber. " + role
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": "Bearer " + GROQ},
        json={"model": "llama-3.3-70b-versatile", "max_tokens": 2048,
              "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}]})
    return r.json()["choices"][0]["message"]["content"]

def send(chat_id, text, kb=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if kb:
        data["reply_markup"] = {"inline_keyboard": kb}
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=data)

def answer_cb(cb_id):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": cb_id})

def check_obuna(user_id):
    if not OBUNA_MAJBURIY:
        return True
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getChatMember",
        params={"chat_id": CHANNEL, "user_id": user_id})
    status = r.json().get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

def bosh_menyu(chat_id):
    send(chat_id, "👤 <b>Siz kimSiz?</b>", [[
        {"text": "👨‍🎓 Talaba", "callback_data": "talaba"}
    ],[
        {"text": "👩‍🏫 O'qituvchi", "callback_data": "oquvchi"}
    ],[
        {"text": "💼 Ofis xodimi", "callback_data": "ofis"}
    ],[
        {"text": "🌟 Hamma uchun", "callback_data": "hamma"}
    ]])

def til_menyusi(chat_id):
    send(chat_id, "🌍 <b>Tilni tanlang / Выберите язык / Choose language</b>", [[
        {"text": "🇺🇿 O'zbek", "callback_data": "til_uz"},
        {"text": "🇷🇺 Русский", "callback_data": "til_ru"},
        {"text": "🇬🇧 English", "callback_data": "til_en"}
    ]])

def ortga_kb(qayerga):
    return [[
        {"text": "◀️ Ortga", "callback_data": qayerga},
        {"text": "🏠 Bosh menyu", "callback_data": "start"}
    ]]

@app.route("/", methods=["POST"])
def webhook():
    d = request.json

    if "callback_query" in d:
        cb = d["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        user_id = cb["from"]["id"]
        ism = cb["from"].get("first_name", "Noma'lum")
        data = cb["data"]
        answer_cb(cb["id"])

        if not check_obuna(user_id) and data != "tekshir":
            send(chat_id, f"📢 Botdan foydalanish uchun kanalga obuna bo'ling:\n{CHANNEL}", [[
                {"text": "📢 Kanalga o'tish", "url": f"https://t.me/{CHANNEL[1:]}"},
                {"text": "✅ Obuna bo'ldim", "callback_data": "tekshir"}
            ]])
            return "ok"

        if data == "tekshir":
            if check_obuna(user_id):
                til_menyusi(chat_id)
            else:
                send(chat_id, "❌ Siz hali obuna bo'lmadingiz!", [[
                    {"text": "📢 Kanalga o'tish", "url": f"https://t.me/{CHANNEL[1:]}"},
                    {"text": "✅ Obuna bo'ldim", "callback_data": "tekshir"}
                ]])
            return "ok"

        if data.startswith("til_"):
            bosh_menyu(chat_id)
            return "ok"

        if data == "start":
            bosh_menyu(chat_id)
            return "ok"if data == "talaba":
            save_user(user_id, ism, "Talaba")
            send(chat_id, "👨‍🎓 <b>Talaba bo'limi</b>", [[
                {"text": "📝 Referat/Kurs ishi", "callback_data": "s_referat"},
                {"text": "📄 Rezyume", "callback_data": "s_rezyume"}
            ],[
                {"text": "💬 Intervyu", "callback_data": "s_intervyu"},
                {"text": "📋 Ariza", "callback_data": "s_ariza"}
            ],[
                {"text": "📖 Diplom ishi", "callback_data": "s_diplom"},
                {"text": "💡 Mavzu tushuntirish", "callback_data": "s_tushuntir"}
            ],[
                {"text": "🃏 Test savollari", "callback_d
