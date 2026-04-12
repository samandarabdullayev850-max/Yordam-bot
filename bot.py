SHEETS_URL = "https://script.google.com/macros/s/AKfycbzRnJbIKgsjpTb8SfNv6nJ4yfzmVoyEg4pdVpQhzqavsx6bNNYrws84FXFB7bEbNEcc1g/exec"

def save_user(user_id, ism, bulim="", xizmat=""):
    try:
        from datetime import datetime
        requests.post(SHEETS_URL, json={
            "user_id": str(user_id),
            "ism": ism,
            "sana": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "bulim": bulim,
            "xizmat": xizmat
        })
    except:
        pass
import requests
from flask import Flask, request

TOKEN = "8381516564:AAHBCKfeR7wy3SQf6ntwsSUVAS1gsvZ1R0o"
GROQ = "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"
ADMIN = "8726418671"
CHANNEL = "@sizning_kanal"
OBUNA_MAJBURIY = False

app = Flask(__name__)

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
        data = cb["data"]
        answer_cb(cb["id"])

        if not check_obuna(user_id) and data != "tekshir":
            send(chat_id, f"📢 Botdan foydalanish uchun kanalga obuna boing:\n{CHANNEL}", [[
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
            return "ok"

        if data == "talaba":
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
                {"text": "🃏 Test savollari", "callback_data": "s_testsavol"},
                {"text": "🔤 Tarjima", "callback_data": "s_tarjima"}
            ],[
                {"text": "🏠 Bosh menyu", "callback_data": "start"}
            ]])

        elif data == "oquvchi":
            send(chat_id, "👩‍🏫 <b>O'qituvchi bo'limi</b>", [[
                {"text": "📋 Texnologik karta", "callback_data": "s_texkarta"},
                {"text": "🎓 Test yaratish", "callback_data": "s_test"}
            ],[
                {"text": "📊 Dars rejasi", "callback_data": "s_darsreja"},
                {"text": "📣 Ota-onalarga xat", "callback_data": "s_xat"}
            ],[
                {"text": "🏆 Tavsifnoma", "callback_data": "s_tavsif"},
                {"text": "📝 Dars tahlili", "callback_data": "s_tahlil"}
            ],[
                {"text": "🎯 Attestatsiya savollari", "callback_data": "s_attestatsiya"},
                {"text": "🔤 Tarjima", "callback_data": "s_tarjima"}
            ],[
                {"text": "🏠 Bosh menyu", "callback_data": "start"}
            ]])

        elif data == "ofis":
            send(chat_id, "💼 <b>Ofis xodimi bo'limi</b>", [[
                {"text": "📱 Reklama matni", "callback_data": "s_reklama"},
                {"text": "📊 Biznes-reja", "callback_data": "s_biznes"}
            ],[
                {"text": "🛍 Mahsulot tavsifi", "callback_data": "s_mahsulot"},
                {"text": "✉️ Email/Xat", "callback_data": "s_email"}
            ],[
                {"text": "📋 Ariza", "callback_data": "s_ariza"},
                {"text": "🔤 Tarjima", "callback_data": "s_tarjima"}
            ],[
                {"text": "🏠 Bosh menyu", "callback_data": "start"}
            ]])

        elif data == "hamma":
            send(chat_id, "🌟 <b>Hamma uchun bo'lim</b>", [[
                {"text": "🎨 Rasm yaratish", "callback_data": "s_rasm"},
                {"text": "💬 Erkin savol", "callback_data": "s_savol"}
            ],[
                {"text": "🌍 Tarjima", "callback_data": "s_tarjima"}
            ],[
                {"text": "🏠 Bosh menyu", "callback_data": "start"}
            ]])

        elif data.startswith("s_"):
            xizmat = data[2:]
            savollar = {
                "referat": ("📝 Referat mavzusini yozing:", "talaba"),
                "rezyume": ("📄 Tajriba va ko'nikmalaringizni yozing:", "talaba"),
                "intervyu": ("💬 Qaysi lavozimga intervyu?", "talaba"),
                "ariza": ("📋 Ariza kimga va nima uchun?", "talaba"),
                "diplom": ("📖 Diplom ishi mavzusini yozing:", "talaba"),
                "tushuntir": ("💡 Qaysi mavzuni tushuntirishimni xohlaysiz?", "talaba"),
                "testsavol": ("🃏 Qaysi fandan test savollari kerak?", "talaba"),
                "tarjima": ("🔤 Matnni yozing (qaysi tildan qaysi tilga):", "hamma"),
                "texkarta": ("📋 Dars mavzusi va sinfni yozing:", "oquvchi"),
                "test": ("🎓 Mavzu va nechta savol kerak?", "oquvchi"),
                "darsreja": ("📊 Dars mavzusi va sinfni yozing:", "oquvchi"),
                "xat": ("📣 Xat mavzusini yozing:", "oquvchi"),
                "tavsif": ("🏆 O'quvchi ismi va sababini yozing:", "oquvchi"),
                "tahlil": ("📝 Dars mavzusi va sinfni yozing — tahlil qilaman:", "oquvchi"),
                "attestatsiya": ("🎯 Fan nomi va sinfni yozing:", "oquvchi"),
                "reklama": ("📱 Mahsulot yoki xizmat haqida yozing:", "ofis"),
                "biznes": ("📊 Biznes g'oyangizni yozing:", "ofis"),
                "mahsulot": ("🛍 Mahsulotingiz haqida yozing:", "ofis"),
                "email": ("✉️ Kimga va nima haqida?", "ofis"),
                "rasm": ("🎨 Rasm uchun tavsif yozing (inglizcha yoki o'zbek tilida):", "hamma"),
                "savol": ("💬 Savolingizni yozing:", "hamma"),
            }
            if xizmat in savollar:
                savol, qayerga = savollar[xizmat]
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": savol,
                    "reply_markup": {"inline_keyboard": ortga_kb(qayerga)}
                })

        return "ok"

    if "message" not in d:
        return "ok"

    chat_id = d["message"]["chat"]["id"]
    user_id = d["message"]["from"]["id"]
    text = d["message"].get("text", "")

    if not check_obuna(user_id) and text != "/start":
        send(chat_id, f"📢 Botdan foydalanish uchun kanalga obuna boing:\n{CHANNEL}", [[
            {"text": "📢 Kanalga o'tish", "url": f"https://t.me/{CHANNEL[1:]}"},
            {"text": "✅ Obuna bo'ldim", "callback_data": "tekshir"}
        ]])
        return "ok"

    if text == "/start":
        til_menyusi(chat_id)
    elif text == "/stats" and str(user_id) == ADMIN:
        send(chat_id, "📊 Bot ishlayapti!")
    elif text.startswith("/reklama ") and str(user_id) == ADMIN:
        send(chat_id, "📢 Reklama yuborilmoqda...")
    else:
        rollar = {
            "referat": "Siz referat yozuvchi mutaxasssissiz. To'liq, sifatli referat yoz.",
            "diplom": "Siz diplom ishi yozuvchi mutaxasssissiz. Batafsil yordam ber.",
            "tushuntir": "Siz o'qituvchisiz. Mavzuni oddiy va tushunarli tushuntir.",
            "testsavol": "Siz test tuzuvchisiz. 10 ta savol va 4 ta javob variantini tuz.",
            "texkarta": "Siz tajribali o'qituvchisiz. To'liq texnologik karta tuz.",
            "test": "Siz test tuzuvchisiz. Savollar va javoblarini tuz.",
            "darsreja": "Siz tajribali o'qituvchisiz. Batafsil dars rejasi tuz.",
            "tahlil": "Siz metodist o'qituvchisiz. Darsni to'liq tahlil qil.",
            "attestatsiya": "Siz attestatsiya mutaxasssissiz. Attestatsiya savollari tuz.",
            "reklama": "Siz professional copywritersiz. Jozibali reklama matni yoz.",
        }
        rol = ""
        send(chat_id, "⏳ Tayyorlanmoqda...")
        javob = ask(text, rol)
        send(chat_id, javob, [[
            {"text": "🏠 Bosh menyu", "callback_data": "start"}
        ]])

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
