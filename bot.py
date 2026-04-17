import os
import requests
from flask import Flask, request
from datetime import datetime
import sqlite3
import google.generativeai as genai
TOKEN = "8381516564:AAHBCKfeR7wy3SQf6ntwsSUVAS1gsvZ1R0o"
GEMINI ="AIzaSyDgjNkEpv4dvfpVK8Q4HSxbeIyakb4dPTw"
genai.configure(api_key=GEMINI)
ADMIN = "8726418671"
SHEETS_URL = "https://script.google.com/macros/s/AKfycbyqCLNmhpZ_4-7J9-d6Jt3s6qxHKpfie4emgXh_tmLGItmrFUYTET5FokrSBCw4b6nQ7g/exec"
OBUNA_MAJBURIY = False
CHANNEL = "@sizning_kanal"

app = Flask(__name__) 

user_lang = {}
user_xizmat = {}

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            ism TEXT,
            sana TEXT,
            bolim TEXT,
            xizmat TEXT
        )
    """)
    conn.commit()
    conn.close() 
   
init_db()

def save_user(user_id, ism, bolim="", xizmat=""):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    sana = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT OR IGNORE INTO users (user_id, ism, sana, bolim, xizmat) VALUES (?, ?, ?, ?, ?)",
              (user_id, ism, sana, bolim, xizmat))
    conn.commit()
    conn.close()
def ask(text, role):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(role + "\n\n" + text)
        return response.text
    except Exception as e:
        print(f"GEMINI XATO: {e}")
        return f"Xato: {str(e)}"
def get_stats():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    jami = c.fetchone()[0]
    bugun = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM users WHERE sana = ?", (bugun,))
    bugungi = c.fetchone()[0]
    c.execute("SELECT bolim, COUNT(*) FROM users GROUP BY bolim")
    bolimlar = c.fetchall()
    conn.close()
    return jami, bugungi, bolimlar

def send_image(chat_id, prompt):
    try:
        clean = prompt.replace(" ", "%20").replace("\n", "")
        url = f"https://image.pollinations.ai/prompt/{clean}?width=512&height=512&nologo=true"
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            json={"chat_id": chat_id, "photo": url, "caption": "Rasm tayyor!"},
            timeout=30)
    except:
        send(chat_id, "Rasm yaratishda xatolik. Qayta urining.")
def send(chat_id, text, kb=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if kb:
        data["reply_markup"] = {"inline_keyboard": kb}
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=data, timeout=10)

def answer_cb(cb_id):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": cb_id}, timeout=5)

def check_obuna(user_id):
    if not OBUNA_MAJBURIY:
        return True
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getChatMember", params={"chat_id": CHANNEL, "user_id": user_id}, timeout=5)
    status = r.json().get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

def til_menyusi(chat_id):
    send(chat_id, "🌍 Tilni tanlang / Choose language / Выберите язык", [[
        {"text": "🇺🇿 O'zbek", "callback_data": "til_uz"},
        {"text": "🇷🇺 Русский", "callback_data": "til_ru"},
        {"text": "🇬🇧 English", "callback_data": "til_en"}
    ]])

def bosh_menyu(chat_id, lang):
    t = {
        "uz": ("👤 Siz kimSiz?", [["👨‍🎓 Talaba", "talaba"], ["👩‍🏫 O'qituvchi", "oquvchi"], ["💼 Ofis xodimi", "ofis"], ["🌟 Hamma uchun", "hamma"]]),
        "ru": ("👤 Кто вы?", [["👨‍🎓 Студент", "talaba"], ["👩‍🏫 Учитель", "oquvchi"], ["💼 Офис", "ofis"], ["🌟 Для всех", "hamma"]]),
        "en": ("👤 Who are you?", [["👨‍🎓 Student", "talaba"], ["👩‍🏫 Teacher", "oquvchi"], ["💼 Office", "ofis"], ["🌟 For all", "hamma"]])
    }.get(lang, ("👤 Siz kimSiz?", [["👨‍🎓 Talaba", "talaba"], ["👩‍🏫 O'qituvchi", "oquvchi"], ["💼 Ofis xodimi", "ofis"], ["🌟 Hamma uchun", "hamma"]]))
    send(chat_id, t[0], [[{"text": i[0], "callback_data": i[1]}] for i in t[1]])

def ortga_kb(lang, qayerga="start"):
    t = {
        "uz": ["◀️ Ortga", "🏠 Bosh menyu"],
        "ru": ["◀️ Назад", "🏠 Главное меню"],
        "en": ["◀️ Back", "🏠 Main menu"]
    }.get(lang, ["◀️ Ortga", "🏠 Bosh menyu"])
    return [[{"text": t[0], "callback_data": qayerga}, {"text": t[1], "callback_data": "start"}]] 
def talaba_menu(chat_id, lang):
    menus = {
        "uz": ("👨‍🎓 Talaba bo'limi", [
            [{"text": "📝 Referat/Kurs ishi", "callback_data": "s_referat"}, {"text": "📄 Rezyume", "callback_data": "s_rezyume"}],
            [{"text": "💬 Intervyu", "callback_data": "s_intervyu"}, {"text": "📋 Ariza", "callback_data": "s_ariza"}],
            [{"text": "📖 Diplom ishi", "callback_data": "s_diplom"}, {"text": "💡 Mavzu tushuntirish", "callback_data": "s_tushuntir"}],
            [{"text": "🃏 Test savollari", "callback_data": "s_testsavol"}, {"text": "🔤 Tarjima", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Bosh menyu", "callback_data": "start"}]]),
        "ru": ("👨‍🎓 Раздел студента", [
            [{"text": "📝 Реферат/Курсовая", "callback_data": "s_referat"}, {"text": "📄 Резюме", "callback_data": "s_rezyume"}],
            [{"text": "💬 Интервью", "callback_data": "s_intervyu"}, {"text": "📋 Заявление", "callback_data": "s_ariza"}],
            [{"text": "📖 Дипломная работа", "callback_data": "s_diplom"}, {"text": "💡 Объяснить тему", "callback_data": "s_tushuntir"}],
            [{"text": "🃏 Тестовые вопросы", "callback_data": "s_testsavol"}, {"text": "🔤 Перевод", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Главное меню", "callback_data": "start"}]]),
        "en": ("👨‍🎓 Student section", [
            [{"text": "📝 Essay/Course work", "callback_data": "s_referat"}, {"text": "📄 Resume", "callback_data": "s_rezyume"}],
            [{"text": "💬 Interview", "callback_data": "s_intervyu"}, {"text": "📋 Application", "callback_data": "s_ariza"}],
            [{"text": "📖 Diploma work", "callback_data": "s_diplom"}, {"text": "💡 Explain topic", "callback_data": "s_tushuntir"}],
            [{"text": "🃏 Test questions", "callback_data": "s_testsavol"}, {"text": "🔤 Translation", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Main menu", "callback_data": "start"}]])
    }
    m = menus.get(lang, menus["uz"])
    send(chat_id, m[0], m[1])

def oquvchi_menu(chat_id, lang):
    menus = {
        "uz": ("👩‍🏫 O'qituvchi bo'limi", [
            [{"text": "📋 Texnologik karta", "callback_data": "s_texkarta"}, {"text": "🎓 Test yaratish", "callback_data": "s_test"}],
            [{"text": "📊 Dars rejasi", "callback_data": "s_darsreja"}, {"text": "📣 Ota-onalarga xat", "callback_data": "s_xat"}],
            [{"text": "🏆 Tavsifnoma", "callback_data": "s_tavsif"}, {"text": "📝 Dars tahlili", "callback_data": "s_tahlil"}],
            [{"text": "🎯 Attestatsiya savollari", "callback_data": "s_attestatsiya"}, {"text": "🔤 Tarjima", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Bosh menyu", "callback_data": "start"}]]),
        "ru": ("👩‍🏫 Раздел учителя", [
            [{"text": "📋 Технологическая карта", "callback_data": "s_texkarta"}, {"text": "🎓 Создать тест", "callback_data": "s_test"}],
            [{"text": "📊 План урока", "callback_data": "s_darsreja"}, {"text": "📣 Письмо родителям", "callback_data": "s_xat"}],
            [{"text": "🏆 Характеристика", "callback_data": "s_tavsif"}, {"text": "📝 Анализ урока", "callback_data": "s_tahlil"}],
            [{"text": "🎯 Вопросы аттестации", "callback_data": "s_attestatsiya"}, {"text": "🔤 Перевод", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Главное меню", "callback_data": "start"}]]),
        "en": ("👩‍🏫 Teacher section", [
            [{"text": "📋 Technology map", "callback_data": "s_texkarta"}, {"text": "🎓 Create test", "callback_data": "s_test"}],
            [{"text": "📊 Lesson plan", "callback_data": "s_darsreja"}, {"text": "📣 Letter to parents", "callback_data": "s_xat"}],
            [{"text": "🏆 Reference letter", "callback_data": "s_tavsif"}, {"text": "📝 Lesson analysis", "callback_data": "s_tahlil"}],
            [{"text": "🎯 Attestation questions", "callback_data": "s_attestatsiya"}, {"text": "🔤 Translation", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Main menu", "callback_data": "start"}]])
    }
    m = menus.get(lang, menus["uz"])
    send(chat_id, m[0], m[1])

def ofis_menu(chat_id, lang):
    menus = {
        "uz": ("💼 Ofis xodimi bo'limi", [
            [{"text": "📱 Reklama matni", "callback_data": "s_reklama"}, {"text": "📊 Biznes-reja", "callback_data": "s_biznes"}],
            [{"text": "🛍 Mahsulot tavsifi", "callback_data": "s_mahsulot"}, {"text": "✉️ Email/Xat", "callback_data": "s_email"}],
            [{"text": "📋 Ariza", "callback_data": "s_ariza"}, {"text": "🔤 Tarjima", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Bosh menyu", "callback_data": "start"}]]),
        "ru": ("💼 Раздел офиса", [
            [{"text": "📱 Рекламный текст", "callback_data": "s_reklama"}, {"text": "📊 Бизнес-план", "callback_data": "s_biznes"}],
            [{"text": "🛍 Описание товара", "callback_data": "s_mahsulot"}, {"text": "✉️ Email/Письмо", "callback_data": "s_email"}],
            [{"text": "📋 Заявление", "callback_data": "s_ariza"}, {"text": "🔤 Перевод", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Главное меню", "callback_data": "start"}]]),
        "en": ("💼 Office section", [
            [{"text": "📱 Ad text", "callback_data": "s_reklama"}, {"text": "📊 Business plan", "callback_data": "s_biznes"}],
            [{"text": "🛍 Product description", "callback_data": "s_mahsulot"}, {"text": "✉️ Email/Letter", "callback_data": "s_email"}],
            [{"text": "📋 Application", "callback_data": "s_ariza"}, {"text": "🔤 Translation", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Main menu", "callback_data": "start"}]])
    }
    m = menus.get(lang, menus["uz"])
    send(chat_id, m[0], m[1])

def hamma_menu(chat_id, lang):
    menus = {
        "uz": ("🌟 Hamma uchun", [
            [{"text": "🎨 Rasm yaratish", "callback_data": "s_rasm"}, {"text": "💬 Savol-javob", "callback_data": "s_savol"}],
            [{"text": "🔤 Tarjima", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Bosh menyu", "callback_data": "start"}]]),
        "ru": ("🌟 Для всех", [
            [{"text": "🎨 Создать картинку", "callback_data": "s_rasm"}, {"text": "💬 Вопрос-ответ", "callback_data": "s_savol"}],
            [{"text": "🔤 Перевод", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Главное меню", "callback_data": "start"}]]),
        "en": ("🌟 For everyone", [
            [{"text": "🎨 Create image", "callback_data": "s_rasm"}, {"text": "💬 Q&A", "callback_data": "s_savol"}],
            [{"text": "🔤 Translation", "callback_data": "s_tarjima"}],
            [{"text": "🏠 Main menu", "callback_data": "start"}]])
    }
    m = menus.get(lang, menus["uz"])
    send(chat_id, m[0], m[1])
SAVOLLAR = {
    "uz": {"referat": "Referat mavzusini yozing:", "rezyume": "Tajriba va konikmalaringizni yozing:", "intervyu": "Qaysi lavozimga intervyu?", "ariza": "Ariza kimga va nima uchun?", "diplom": "Diplom ishi mavzusini yozing:", "tushuntir": "Qaysi mavzuni tushuntirishimni xohlaysiz?", "testsavol": "Qaysi fandan test savollari kerak?", "tarjima": "Matnni yozing qaysi tildan qaysi tilga:", "texkarta": "Dars mavzusi va sinfni yozing:", "test": "Mavzu va nechta savol kerak?", "darsreja": "Dars mavzusi va sinfni yozing:", "xat": "Xat mavzusini yozing:", "tavsif": "Oquvchi ismi va sababini yozing:", "tahlil": "Dars mavzusi va sinfni yozing:", "attestatsiya": "Fan nomi va sinfni yozing:", "reklama": "Mahsulot yoki xizmat haqida yozing:", "biznes": "Biznes goyangizni yozing:", "mahsulot": "Mahsulotingiz haqida yozing:", "email": "Kimga va nima haqida?", "rasm": "Rasm uchun tavsif yozing:", "savol": "Savolingizni yozing:"},
    "ru": {"referat": "Напишите тему реферата:", "rezyume": "Напишите опыт и навыки:", "intervyu": "На какую должность интервью?", "ariza": "Кому и для чего заявление?", "diplom": "Напишите тему дипломной работы:", "tushuntir": "Какую тему объяснить?", "testsavol": "По какому предмету тест?", "tarjima": "Напишите текст и с какого на какой язык:", "texkarta": "Напишите тему урока и класс:", "test": "Тема и количество вопросов?", "darsreja": "Напишите тему урока и класс:", "xat": "Тема письма родителям:", "tavsif": "Имя ученика и причина:", "tahlil": "Напишите тему урока и класс:", "attestatsiya": "Предмет и класс:", "reklama": "О товаре или услуге:", "biznes": "Напишите бизнес-идею:", "mahsulot": "О вашем товаре:", "email": "Кому и о чём письмо?", "rasm": "Опишите картинку:", "savol": "Напишите вопрос:"},
    "en": {"referat": "Write essay topic:", "rezyume": "Write your experience and skills:", "intervyu": "What position is the interview for?", "ariza": "Who is the application for?", "diplom": "Write diploma work topic:", "tushuntir": "What topic to explain?", "testsavol": "Which subject test questions?", "tarjima": "Write text and from which language to which:", "texkarta": "Write lesson topic and class:", "test": "Topic and number of questions?", "darsreja": "Write lesson topic and class:", "xat": "Topic of letter to parents:", "tavsif": "Student name and reason:", "tahlil": "Write lesson topic and class:", "attestatsiya": "Subject and class:", "reklama": "About product or service:", "biznes": "Write your business idea:", "mahsulot": "About your product:", "email": "To whom and about what?", "rasm": "Describe the image:", "savol": "Write your question:"}
}

ROLLAR = {
    "uz": {"referat": "Sen referat yozuvchi mutaxasssissan. Tolik sifatli referat yoz. Kirish asosiy qism va xulosa bolsin. OZBEKCHA yoz.", "rezyume": "Sen professional rezyume yozuvchisan. Chiroyli rezyume tuz. OZBEKCHA yoz.", "intervyu": "Sen intervyuga tayyorgarlik mutaxasssissan. Savollar va javoblarni yoz. OZBEKCHA yoz.", "ariza": "Sen rasmiy hujjatlar mutaxasssissan. Togri rasmiy ariza yoz. OZBEKCHA yoz.", "diplom": "Sen diplom ishi mutaxasssissan. Diplom ishiga yordam ber. OZBEKCHA yoz.", "tushuntir": "Sen tajribali oquvchisan. Mavzuni oddiy va tushunarli tushuntir. OZBEKCHA yoz.", "testsavol": "Sen test tuzuvchisan. 10 ta savol va 4 ta javob varianti tuz. OZBEKCHA yoz.", "tarjima": "Sen professional tarjimonsan. Matnni aniq tarjima qil.", "texkarta": "Sen tajribali oquvchisan. Tolik texnologik karta tuz. OZBEKCHA yoz.", "test": "Sen test tuzuvchisan. Savollar va javoblarini tuz. OZBEKCHA yoz.", "darsreja": "Sen tajribali oquvchisan. Batafsil dars rejasi tuz. OZBEKCHA yoz.", "xat": "Sen sinf rahbarisisan. Ota-onalarga rasmiy xat yoz. OZBEKCHA yoz.", "tavsif": "Sen maktab mamuryatisan. Rasmiy tavsifnoma yoz. OZBEKCHA yoz.", "tahlil": "Sen metodistsan. Darsni tolik tahlil qil. OZBEKCHA yoz.", "attestatsiya": "Sen attestatsiya mutaxasssissan. Attestatsiya savollari tuz. OZBEKCHA yoz.", "reklama": "Sen professional kopiraytersan. Jozibali reklama matni yoz. OZBEKCHA yoz.", "biznes": "Sen biznes maslahatchisan. Batafsil biznes-reja tuz. OZBEKCHA yoz.", "mahsulot": "Sen marketing mutaxasssissan. Jozibali tavsif yoz. OZBEKCHA yoz.", "email": "Sen professional email yozuvchisan. Rasmiy email yoz. OZBEKCHA yoz.", "rasm": "Rasmni batafsil tasvirla. OZBEKCHA yoz.", "savol": "Sen aqlli yordamchisan. Savolga tolik va aniq javob ber. OZBEKCHA yoz."},
    "ru": {"referat": "Ты специалист по написанию рефератов. Напиши полный качественный реферат. Отвечай НА РУССКОМ.", "rezyume": "Ты профессиональный составитель резюме. Создай красивое резюме. Отвечай НА РУССКОМ.", "intervyu": "Ты специалист по подготовке к интервью. Напиши вопросы и ответы. Отвечай НА РУССКОМ.", "ariza": "Ты специалист по деловым документам. Напиши официальное заявление. Отвечай НА РУССКОМ.", "diplom": "Ты специалист по дипломным работам. Помоги с дипломной работой. Отвечай НА РУССКОМ.", "tushuntir": "Ты опытный учитель. Объясни тему просто и понятно. Отвечай НА РУССКОМ.", "testsavol": "Ты составитель тестов. Создай 10 вопросов с 4 вариантами ответов. Отвечай НА РУССКОМ.", "tarjima": "Ты профессиональный переводчик. Переведи текст точно.", "texkarta": "Ты опытный учитель. Составь полную технологическую карту. Отвечай НА РУССКОМ.", "test": "Ты составитель тестов. Создай вопросы с ответами. Отвечай НА РУССКОМ.", "darsreja": "Ты опытный учитель. Составь подробный план урока. Отвечай НА РУССКОМ.", "xat": "Ты классный руководитель. Напиши официальное письмо родителям. Отвечай НА РУССКОМ.", "tavsif": "Ты администратор школы. Напиши официальную характеристику. Отвечай НА РУССКОМ.", "tahlil": "Ты методист. Сделай полный анализ урока. Отвечай НА РУССКОМ.", "attestatsiya": "Ты специалист по аттестации. Составь вопросы для аттестации. Отвечай НА РУССКОМ.", "reklama": "Ты профессиональный копирайтер. Напиши привлекательный рекламный текст. Отвечай НА РУССКОМ.", "biznes": "Ты бизнес-консультант. Составь подробный бизнес-план. Отвечай НА РУССКОМ.", "mahsulot": "Ты маркетолог. Напиши привлекательное описание. Отвечай НА РУССКОМ.", "email": "Ты профессиональный составитель писем. Напиши официальное письмо. Отвечай НА РУССКОМ.", "rasm": "Опиши картинку подробно. Отвечай НА РУССКОМ.", "savol": "Ты умный помощник. Ответь на вопрос полно и точно. Отвечай НА РУССКОМ."},
    "en": {"referat": "You are an essay writing specialist. Write a complete quality essay. Answer IN ENGLISH.", "rezyume": "You are a professional resume writer. Create a beautiful resume. Answer IN ENGLISH.", "intervyu": "You are an interview preparation specialist. Write questions and answers. Answer IN ENGLISH.", "ariza": "You are a business document specialist. Write an official application. Answer IN ENGLISH.", "diplom": "You are a diploma work specialist. Help with diploma work. Answer IN ENGLISH.", "tushuntir": "You are an experienced teacher. Explain the topic simply. Answer IN ENGLISH.", "testsavol": "You are a test maker. Create 10 questions with 4 answer options. Answer IN ENGLISH.", "tarjima": "You are a professional translator. Translate the text accurately.", "texkarta": "You are an experienced teacher. Create a complete technology map. Answer IN ENGLISH.", "test": "You are a test maker. Create questions with answers. Answer IN ENGLISH.", "darsreja": "You are an experienced teacher. Create a detailed lesson plan. Answer IN ENGLISH.", "xat": "You are a class teacher. Write an official letter to parents. Answer IN ENGLISH.", "tavsif": "You are a school administrator. Write an official reference letter. Answer IN ENGLISH.", "tahlil": "You are a methodologist. Do a complete lesson analysis. Answer IN ENGLISH.", "attestatsiya": "You are an attestation specialist. Create attestation questions. Answer IN ENGLISH.", "reklama": "You are a professional copywriter. Write attractive ad text. Answer IN ENGLISH.", "biznes": "You are a business consultant. Create a detailed business plan. Answer IN ENGLISH.", "mahsulot": "You are a marketing specialist. Write an attractive description. Answer IN ENGLISH.", "email": "You are a professional email writer. Write an official email. Answer IN ENGLISH.", "rasm": "Describe the image in detail. Answer IN ENGLISH.", "savol": "You are a smart assistant. Answer the question fully and accurately. Answer IN ENGLISH."}
}

@app.route("/", methods=["POST"])
def webhook():
    d = request.json
    if not d:
        return "ok"
    if "callback_query" in d:
        cb = d["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        user_id = cb["from"]["id"]
        ism = cb["from"].get("first_name", "Foydalanuvchi")
        data = cb["data"]
        lang = user_lang.get(user_id, "uz")
        answer_cb(cb["id"])

        if not check_obuna(user_id) and data != "tekshir":
            send(chat_id, "Botdan foydalanish uchun kanalga obuna boling!", [[{"text": "Kanalga otish", "url": f"https://t.me/{CHANNEL[1:]}"},{"text": "Obuna boldim", "callback_data": "tekshir"}]])
            return "ok"

        if data == "tekshir":
            if check_obuna(user_id):
                til_menyusi(chat_id)
            else:
                send(chat_id, "Siz hali obuna bolmadingiz!", [[{"text": "Kanalga otish", "url": f"https://t.me/{CHANNEL[1:]}"},{"text": "Obuna boldim", "callback_data": "tekshir"}]])
            return "ok"

        if data == "til_uz":
            user_lang[user_id] = "uz"
            bosh_menyu(chat_id, "uz")
            return "ok"
        if data == "til_ru":
            user_lang[user_id] = "ru"
            bosh_menyu(chat_id, "ru")
            return "ok"
        if data == "til_en":
            user_lang[user_id] = "en"
            bosh_menyu(chat_id, "en")
            return "ok"
        if data == "start":
            bosh_menyu(chat_id, lang)
            return "ok"
        if data == "talaba":
            save_user(user_id, ism, "Talaba")
            talaba_menu(chat_id, lang)
            return "ok"
        if data == "oquvchi":
            save_user(user_id, ism, "Oquvchi")
            oquvchi_menu(chat_id, lang)
            return "ok"
        if data == "ofis":
            save_user(user_id, ism, "Ofis")
            ofis_menu(chat_id, lang)
            return "ok"
        if data == "hamma":
            save_user(user_id, ism, "Hamma")
            hamma_menu(chat_id, lang)
            return "ok"

        if data.startswith("s_"):
            xizmat = data[2:]
            user_xizmat[user_id] = xizmat
            savol = SAVOLLAR.get(lang, SAVOLLAR["uz"]).get(xizmat, "Yozing:")
            save_user(user_id, ism, "", xizmat)
            talaba_xizmatlar = ["referat", "rezyume", "intervyu", "ariza", "diplom", "tushuntir", "testsavol"]
            oquvchi_xizmatlar = ["texkarta", "test", "darsreja", "xat", "tavsif", "tahlil", "attestatsiya"]
            ofis_xizmatlar = ["reklama", "biznes", "mahsulot", "email"]
            if xizmat in talaba_xizmatlar:
                qayerga = "talaba"
            elif xizmat in oquvchi_xizmatlar:
                qayerga = "oquvchi"
            elif xizmat in ofis_xizmatlar:
                qayerga = "ofis"
            else:
                qayerga = "hamma"
            send(chat_id, savol, ortga_kb(lang, qayerga))
            return "ok"

        return "ok"

    if "message" not in d:
        return "ok"

    chat_id = d["message"]["chat"]["id"]
    user_id = d["message"]["from"]["id"]
    ism = d["message"]["from"].get("first_name", "Foydalanuvchi")
    text = d["message"].get("text", "")
    lang = user_lang.get(user_id, "uz")

    if not check_obuna(user_id) and text != "/start":
        send(chat_id, "Botdan foydalanish uchun kanalga obuna boling!", [[{"text": "Kanalga otish", "url": f"https://t.me/{CHANNEL[1:]}"},{"text": "Obuna boldim", "callback_data": "tekshir"}]])
        return "ok"

    if text == "/start":
        save_user(user_id, ism)
        til_menyusi(chat_id)
    elif text == "/stats" and str(user_id) == ADMIN:
        jami, bugungi, bolimlar = get_stats()
        bolim_text = "\n".join([f"  • {b[0] or 'Noaniq'}: {b[1]} ta" for b in bolimlar])
        send(chat_id,
            f"📊 <b>Bot Statistikasi</b>\n\n"
            f"👥 Jami foydalanuvchilar: <b>{jami}</b>\n"
            f"🆕 Bugun qo'shilganlar: <b>{bugungi}</b>\n\n"
            f"📂 Bo'limlar bo'yicha:\n{bolim_text}"
            ) 
    elif text.startswith("/broadcast ") and str(user_id) == ADMIN:
        xabar = text[11:]
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        users = c.fetchall()
        conn.close()
        yuborildi = 0
        for u in users:
            try:
                send(u[0], xabar)
                yuborildi += 1
            except:
                pass
        send(chat_id, f"✅ {yuborildi} ta foydalanuvchiga yuborildi!")
    elif text.startswith("/reklama ") and str(user_id) == ADMIN:
        send(chat_id, "Reklama yuborilmoqda...")
    else:
        xizmat = user_xizmat.get(user_id, "savol")
        if xizmat == "rasm":
            clean = text.replace(" ", "%20").replace("\n", "")
            url = f"https://image.pollinations.ai/prompt/{clean}?width=512&height=512&nologo=true"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                json={"chat_id": chat_id, "photo": url, "caption": "Rasm tayyor!"}, timeout=30)
            menyu_text = {"uz": "Bosh menyu", "ru": "Glavnoe menyu", "en": "Main menu"}.get(lang, "Bosh menyu")
            send(chat_id, "Yana rasm yaratish uchun tavsif yozing!", [[{"text": menyu_text, "callback_data": "start"}]])
        else:
            role = ROLLAR.get(lang, ROLLAR["uz"]).get(xizmat, "Sen aqlli yordamchisan.")
            try:
                javob = ask(text, role)
            except:
                javob = "Xatolik yuz berdi. Qayta urinib ko'ring."
            menyu_text = {"uz": "Bosh menyu", "ru": "Glavnoe menyu", "en": "Main menu"}.get(lang, "Bosh menyu")
            send(chat_id, javob, [[{"text": menyu_text, "callback_data": "start"}]])
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
