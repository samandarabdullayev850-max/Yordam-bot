import os
import requests
from flask import Flask, request
from datetime import datetime

TOKEN = "8381516564:AAHBCKfeR7wy3SQf6ntwsSUVAS1gsvZ1R0o"
GROQ = "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"
ADMIN = "8726418671"
SHEETS_URL = "https://script.google.com/macros/s/AKfycbzRnJbIKgsjpTb8SfNv6nJ4yfzmVoyEg4pdVpQhzqavsx6bNNYrws84FXFB7bEbNEcc1g/exec"
OBUNA_MAJBURIY = False
CHANNEL = "@sizning_kanal"

app = Flask(__name__)
user_lang = {}

def save_user(user_id, ism, bulim="", xizmat=""):
    try:
        requests.post(SHEETS_URL, json={
            "user_id": str(user_id),
            "ism": ism,
            "sana": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "bulim": bulim,
            "xizmat": xizmat
        }, timeout=3)
    except:
        pass

def ask(text, role=""):
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": "Bearer " + GROQ},
        json={"model": "llama-3.3-70b-versatile", "max_tokens": 2048,
              "messages": [{"role": "system", "content": role}, {"role": "user", "content": text}]},
        timeout=30)
    return r.json()["choices"][0]["message"]["content"]

def send(chat_id, text, kb=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if kb:
        data["reply_markup"] = {"inline_keyboard": kb}
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=data, timeout=10)

def answer_cb(cb_id):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
        json={"callback_query_id": cb_id}, timeout=5)

def check_obuna(user_id):
    if not OBUNA_MAJBURIY:
        return True
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getChatMember",
        params={"chat_id": CHANNEL, "user_id": user_id}, timeout=5)
    status = r.json().get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

def til_menyusi(chat_id):
    send(chat_id, "Tilni tanlang / Выберите язык / Choose language", [[
        {"text": "O'zbek", "callback_data": "til_uz"},
        {"text": "Русский", "callback_data": "til_ru"},
        {"text": "English", "callback_data": "til_en"}
    ]])

def bosh_menyu(chat_id, lang="uz"):
    if lang == "ru":
        text = "Кто вы?"
        t = [["Студент", "talaba"], ["Учитель", "oquvchi"], ["Офис", "ofis"], ["Для всех", "hamma"]]
    elif lang == "en":
        text = "Who are you?"
        t = [["Student", "talaba"], ["Teacher", "oquvchi"], ["Office", "ofis"], ["For all", "hamma"]]
    else:
        text = "Siz kimSiz?"
        t = [["Talaba", "talaba"], ["O'qituvchi", "oquvchi"], ["Ofis xodimi", "ofis"], ["Hamma uchun", "hamma"]]
    send(chat_id, text, [[{"text": i[0], "callback_data": i[1]}] for i in t])

def ortga_kb(qayerga, lang="uz"):
    if lang == "ru":
        return [[{"text": "Назад", "callback_data": qayerga}, {"text": "Главное меню", "callback_data": "start"}]]
    elif lang == "en":
        return [[{"text": "Back", "callback_data": qayerga}, {"text": "Main menu", "callback_data": "start"}]]
    else:
        return [[{"text": "Ortga", "callback_data": qayerga}, {"text": "Bosh menyu", "callback_data": "start"}]]    def talaba_menu(chat_id, lang="uz"):
    if lang == "ru":
        text = "Раздел студента"
        kb = [[
            {"text": "Реферат/Курсовая", "callback_data": "s_referat"},
            {"text": "Резюме", "callback_data": "s_rezyume"}
        ],[
            {"text": "Интервью", "callback_data": "s_intervyu"},
            {"text": "Заявление", "callback_data": "s_ariza"}
        ],[
            {"text": "Дипломная работа", "callback_data": "s_diplom"},
            {"text": "Объяснить тему", "callback_data": "s_tushuntir"}
        ],[
            {"text": "Тестовые вопросы", "callback_data": "s_testsavol"},
            {"text": "Перевод", "callback_data": "s_tarjima"}
        ],[
            {"text": "Главное меню", "callback_data": "start"}
        ]]
    elif lang == "en":
        text = "Student section"
        kb = [[
            {"text": "Essay/Course work", "callback_data": "s_referat"},
            {"text": "Resume", "callback_data": "s_rezyume"}
        ],[
            {"text": "Interview", "callback_data": "s_intervyu"},
            {"text": "Application", "callback_data": "s_ariza"}
        ],[
            {"text": "Diploma work", "callback_data": "s_diplom"},
            {"text": "Explain topic", "callback_data": "s_tushuntir"}
        ],[
            {"text": "Test questions", "callback_data": "s_testsavol"},
            {"text": "Translation", "callback_data": "s_tarjima"}
        ],[
            {"text": "Main menu", "callback_data": "start"}
        ]]
    else:
        text = "Talaba bolimi"
        kb = [[
            {"text": "Referat/Kurs ishi", "callback_data": "s_referat"},
            {"text": "Rezyume", "callback_data": "s_rezyume"}
        ],[
            {"text": "Intervyu", "callback_data": "s_intervyu"},
            {"text": "Ariza", "callback_data": "s_ariza"}
        ],[
            {"text": "Diplom ishi", "callback_data": "s_diplom"},
            {"text": "Mavzu tushuntirish", "callback_data": "s_tushuntir"}
        ],[
            {"text": "Test savollari", "callback_data": "s_testsavol"},
            {"text": "Tarjima", "callback_data": "s_tarjima"}
        ],[
            {"text": "Bosh menyu", "callback_data": "start"}
        ]]
    send(chat_id, text, kb)

def oquvchi_menu(chat_id, lang="uz"):
    if lang == "ru":
        text = "Раздел учителя"
        kb = [[
            {"text": "Технологическая карта", "callback_data": "s_texkarta"},
            {"text": "Создать тест", "callback_data": "s_test"}
        ],[
            {"text": "План урока", "callback_data": "s_darsreja"},
            {"text": "Письмо родителям", "callback_data": "s_xat"}
        ],[
            {"text": "Характеристика", "callback_data": "s_tavsif"},
            {"text": "Анализ урока", "callback_data": "s_tahlil"}
        ],[
            {"text": "Вопросы аттестации", "callback_data": "s_attestatsiya"},
            {"text": "Перевод", "callback_data": "s_tarjima"}
        ],[
            {"text": "Главное меню", "callback_data": "start"}
        ]]
    elif lang == "en":
        text = "Teacher section"
        kb = [[
            {"text": "Technology map", "callback_data": "s_texkarta"},
            {"text": "Create test", "callback_data": "s_test"}
        ],[
            {"text": "Lesson plan", "callback_data": "s_darsreja"},
            {"text": "Letter to parents", "callback_data": "s_xat"}
        ],[
            {"text": "Reference letter", "callback_data": "s_tavsif"},
            {"text": "Lesson analysis", "callback_data": "s_tahlil"}
        ],[
            {"text": "Attestation questions", "callback_data": "s_attestatsiya"},
            {"text": "Translation", "callback_data": "s_tarjima"}
        ],[
            {"text": "Main menu", "callback_data": "start"}
        ]]
    else:
        text = "O'qituvchi bolimi"
        kb = [[
            {"text": "Texnologik karta", "callback_data": "s_texkarta"},
            {"text": "Test yaratish", "callback_data": "s_test"}
        ],[
            {"text": "Dars rejasi", "callback_data": "s_darsreja"},
            {"text": "Ota-onalarga xat", "callback_data": "s_xat"}
        ],[
            {"text": "Tavsifnoma", "callback_data": "s_tavsif"},
            {"text": "Dars tahlili", "callback_data": "s_tahlil"}
        ],[
            {"text": "Attestatsiya savollari", "callback_data": "s_attestatsiya"},
            {"text": "Tarjima", "callback_data": "s_tarjima"}
        ],[
            {"text": "Bosh menyu", "callback_data": "start"}
        ]]
    send(chat_id, text, kb)

def ofis_menu(chat_id, lang="uz"):
    if lang == "ru":
        text = "Раздел офиса"
        kb = [[
            {"text": "Рекламный текст", "callback_data": "s_reklama"},
            {"text": "Бизнес-план", "callback_data": "s_biznes"}
        ],[
            {"text": "Описание товара", "callback_data": "s_mahsulot"},
            {"text": "Email/Письмо", "callback_data": "s_email"}
        ],[
            {"text": "Заявление", "callback_data": "s_ariza"},
            {"text": "Перевод", "callback_data": "s_tarjima"}
        ],[
            {"text": "Главное меню", "callback_data": "start"}
        ]]
    elif lang == "en":
        text = "Office section"
        kb = [[
            {"text": "Ad text", "callback_data": "s_reklama"},
            {"text": "Business plan", "callback_data": "s_biznes"}
        ],[
            {"text": "Product description", "callback_data": "s_mahsulot"},
            {"text": "Email/Letter", "callback_data": "s_email"}
        ],[
            {"text": "Application", "callback_data": "s_ariza"},
            {"text": "Translation", "callback_data": "s_tarjima"}
        ],[
            {"text": "Main menu", "callback_data": "start"}
        ]]
    else:
        text = "Ofis xodimi bolimi"
        kb = [[
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
        ]]
    send(chat_id, text, kb)

def hamma_menu(chat_id, lang="uz"):
    if lang == "ru":
        text = "Для всех"
        kb = [[
            {"text": "Создать картинку", "callback_data": "s_rasm"},
            {"text": "Вопрос-ответ", "callback_data": "s_savol"}
        ],[
            {"text": "Перевод", "callback_data": "s_tarjima"}
        ],[
            {"text": "Главное меню", "callback_data": "start"}
        ]]
    elif lang == "en":
        text = "For everyone"
        kb = [[
            {"text": "Create image", "callback_data": "s_rasm"},
            {"text": "Q&A", "callback_data": "s_savol"}
        ],[
            {"text": "Translation", "callback_data": "s_tarjima"}
        ],[
            {"text": "Main menu", "callback_data": "start"}
        ]]
    else:
        text = "Hamma uchun"
        kb = [[
            {"text": "Rasm yaratish", "callback_data": "s_rasm"},
            {"text": "Savol-javob", "callback_data": "s_savol"}
        ],[
            {"text": "Tarjima", "callback_data": "s_tarjima"}
        ],[
            {"text": "Bosh menyu", "callback_data": "start"}
        ]]
    send(chat_id, text, kb)    def get_savol(xizmat, lang="uz"):
    savollar = {
        "uz": {
            "referat": "Referat mavzusini yozing:",
            "rezyume": "Tajriba va konikmalaringizni yozing:",
            "intervyu": "Qaysi lavozimga intervyu?",
            "ariza": "Ariza kimga va nima uchun?",
            "diplom": "Diplom ishi mavzusini yozing:",
            "tushuntir": "Qaysi mavzuni tushuntirishimni xohlaysiz?",
            "testsavol": "Qaysi fandan test savollari kerak?",
            "tarjima": "Matnni yozing qaysi tildan qaysi tilga:",
            "texkarta": "Dars mavzusi va sinfni yozing:",
            "test": "Mavzu va nechta savol kerak?",
            "darsreja": "Dars mavzusi va sinfni yozing:",
            "xat": "Xat mavzusini yozing:",
            "tavsif": "Oquvchi ismi va sababini yozing:",
            "tahlil": "Dars mavzusi va sinfni yozing:",
            "attestatsiya": "Fan nomi va sinfni yozing:",
            "reklama": "Mahsulot yoki xizmat haqida yozing:",
            "biznes": "Biznes goyangizni yozing:",
            "mahsulot": "Mahsulotingiz haqida yozing:",
            "email": "Kimga va nima haqida?",
            "rasm": "Rasm uchun tavsif yozing:",
            "savol": "Savolingizni yozing:"
        },
        "ru": {
            "referat": "Напишите тему реферата:",
            "rezyume": "Напишите опыт и навыки:",
            "intervyu": "На какую должность интервью?",
            "ariza": "Кому и для чего заявление?",
            "diplom": "Напишите тему дипломной работы:",
            "tushuntir": "Какую тему объяснить?",
            "testsavol": "По какому предмету тест?",
            "tarjima": "Напишите текст и с какого на какой язык:",
            "texkarta": "Напишите тему урока и класс:",
            "test": "Тема и количество вопросов?",
            "darsreja": "Напишите тему урока и класс:",
            "xat": "Тема письма родителям:",
            "tavsif": "Имя ученика и причина:",
            "tahlil": "Напишите тему урока и класс:",
            "attestatsiya": "Предмет и класс:",
            "reklama": "О товаре или услуге:",
            "biznes": "Напишите бизнес-идею:",
            "mahsulot": "О вашем товаре:",
            "email": "Кому и о чём письмо?",
            "rasm": "Опишите картинку:",
            "savol": "Напишите вопрос:"
        },
        "en": {
            "referat": "Write essay topic:",
            "rezyume": "Write your experience and skills:",
            "intervyu": "What position is the interview for?",
            "ariza": "Who is the application for?",
            "diplom": "Write diploma work topic:",
            "tushuntir": "What topic to explain?",
            "testsavol": "Which subject test questions?",
            "tarjima": "Write text and from which language to which:",
            "texkarta": "Write lesson topic and class:",
            "test": "Topic and number of questions?",
            "darsreja": "Write lesson topic and class:",
            "xat": "Topic of letter to parents:",
            "tavsif": "Student name and reason:",
            "tahlil": "Write lesson topic and class:",
            "attestatsiya": "Subject and class:",
            "reklama": "About product or service:",
            "biznes": "Write your business idea:",
            "mahsulot": "About your product:",
            "email": "To whom and about what?",
            "rasm": "Describe the image:",
            "savol": "Write your question:"
        }
    }
    return savollar.get(lang, savollar["uz"]).get(xizmat, "Yozing:")

def get_role(xizmat, lang="uz"):
    if lang == "ru":
        rollar = {
            "referat": "Ti specialist po napisaniyu referatov. Napishi polniy kachestveniy referat.",
            "rezyume": "Ti professional po napisaniyu rezyume. Sozday krasivoe rezyume.",
            "intervyu": "Ti specialist po podgotovke k intervyu. Napishi voprosi i otveti.",
            "ariza": "Ti specialist po delovim dokumentam. Napishi oficialnoe zayavlenie.",
            "diplom": "Ti specialist po diplomnim rabotam. Pomogi s diplomnoy rabotoy.",
            "tushuntir": "Ti opitny uchitel. Obyasni temu prosto i ponyatno.",
            "testsavol": "Ti sostavitel testov. Sozday 10 voprosov s 4 variantami otvetov.",
            "tarjima": "Ti professional perevodchik. Perevedi tekst tochno.",
            "texkarta": "Ti opitny uchitel. Sostavь polnuyu tekhnologicheskuyu kartu.",
            "test": "Ti sostavitel testov. Sozday voprosi s otvetami.",
            "darsreja": "Ti opitny uchitel. Sostavь podrobniy plan uroka.",
            "xat": "Ti klassniy rukovoditel. Napishi oficialnoe pismo roditelyam.",
            "tavsif": "Ti administrator shkoli. Napishi oficialnuyu harakteristiku.",
            "tahlil": "Ti metodist. Sdelай polniy analiz uroka.",
            "attestatsiya": "Ti specialist po attestatsii. Sostavь voprosi dlya attestatsii.",
            "reklama": "Ti professional kopirayterz. Napishi privlekatelniy reklamny tekst.",
            "biznes": "Ti biznes-konsultant. Sostavь podrobniy biznes-plan.",
            "mahsulot": "Ti marketing specialist. Napishi privlekatelnoe opisanie.",
            "email": "Ti professional po delovoy perepiske. Napishi oficialnoye pismo.",
            "rasm": "Opishi kartinku podrobno.",
            "savol": "Ti umniy asistent. Otvet na vopros polno i tochno."
        }
    elif lang == "en":
        rollar = {
            "referat": "You are an essay writing specialist. Write a complete quality essay.",
            "rezyume": "You are a professional resume writer. Create a beautiful resume.",
            "intervyu": "You are an interview preparation specialist. Write questions and answers.",
            "ariza": "You are a business document specialist. Write an official application.",
            "diplom": "You are a diploma work specialist. Help with diploma work.",
            "tushuntir": "You are an experienced teacher. Explain the topic simply.",
            "testsavol": "You are a test maker. Create 10 questions with 4 answer options.",
            "tarjima": "You are a professional translator. Translate the text accurately.",
            "texkarta": "You are an experienced teacher. Create a complete technology map.",
            "test": "You are a test maker. Create questions with answers.",
            "darsreja": "You are an experienced teacher. Create a detailed lesson plan.",
            "xat": "You are a class teacher. Write an official letter to parents.",
            "tavsif": "You are a school administrator. Write an official reference letter.",
            "tahlil": "You are a methodologist. Do a complete lesson analysis.",
            "attestatsiya": "You are an attestation specialist. Create attestation questions.",
            "reklama": "You are a professional copywriter. Write attractive ad text.",
            "biznes": "You are a business consultant. Create a detailed business plan.",
            "mahsulot": "You are a marketing specialist. Write an attractive description.",
            "email": "You are a professional email writer. Write an official email.",
            "rasm": "Describe the image in detail.",
            "savol": "You are a smart assistant. Answer the question fully and accurately."
        }
    else:
        rollar = {
            "referat": "Sen referat yozuvchi mutaxasssissan. Tolik sifatli referat yoz. Kirish asosiy qism va xulosa bolsin.",
            "rezyume": "Sen professional rezyume yozuvchisan. Chiroyli rezyume tuz.",
            "intervyu": "Sen intervyuga tayyorgarlik mutaxasssissan. Savollar va javoblarni yoz.",
            "ariza": "Sen rasmiy hujjatlar mutaxasssissan. Togri rasmiy ariza yoz.",
            "diplom": "Sen diplom ishi mutaxasssissan. Diplom ishiga yordam ber.",
            "tushuntir": "Sen tajribali oquvchisan. Mavzuni oddiy va tushunarli tushuntir.",
            "testsavol": "Sen test tuzuvchisan. 10 ta savol va 4 ta javob varianti tuz.",
            "tarjima": "Sen professional tarjimonsan. Matnni aniq tarjima qil.",
            "texkarta": "Sen tajribali oquvchisan. Tolik texnologik karta tuz.",
            "test": "Sen test tuzuvchisan. Savollar va javoblarini tuz.",
            "darsreja": "Sen tajribali oquvchisan. Batafsil dars rejasi tuz.",
            "xat": "Sen sinf rahbarisisan. Ota-onalarga rasmiy xat yoz.",
            "tavsif": "Sen maktab mamuryatisan. Rasmiy tavsifnoma yoz.",
            "tahlil": "Sen metodistsan. Darsni tolik tahlil qil.",
            "attestatsiya": "Sen attestatsiya mutaxasssissan. Attestatsiya savollari tuz.",
            "reklama": "Sen professional kopiraytersan. Jozibali reklama matni yoz.",
            "biznes": "Sen biznes maslahatchisan. Batafsil biznes-reja tuz.",
            "mahsulot": "Sen marketing mutaxasssissan. Jozibali tavsif yoz.",
            "email": "Sen professional email yozuvchisan. Rasmiy email yoz.",
            "rasm": "Rasmni batafsil tasvirla.",
            "savol": "Sen aqlli yordamchisan. Savolga tolik va aniq javob ber."
        }
    return rollar.get(xizmat, "Yordamchi bol.")    @app.route("/", methods=["POST"])
def webhook():
    d = request.json

    if "callback_query" in d:
        cb = d["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        user_id = cb["from"]["id"]
        ism = cb["from"].get("first_name", "Foydalanuvchi")
        data = cb["data"]
        lang = user_lang.get(user_id, "uz")
        answer_cb(cb["id"])

        if not check_obuna(user_id) and data != "tekshir":
            send(chat_id, "Botdan foydalanish uchun kanalga obuna boling!", [[
                {"text": "Kanalga otish", "url": f"https://t.me/{CHANNEL[1:]}"},
                {"text": "Obuna boldim", "callback_data": "tekshir"}
            ]])
            return "ok"

        if data == "tekshir":
            if check_obuna(user_id):
                til_menyusi(chat_id)
            else:
                send(chat_id, "Siz hali obuna bolmadingiz!", [[
                    {"text": "Kanalga otish", "url": f"https://t.me/{CHANNEL[1:]}"},
                    {"text": "Obuna boldim", "callback_data": "tekshir"}
                ]])
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
            savol = get_savol(xizmat, lang)
            save_user(user_id, ism, "", xizmat)
            send(chat_id, savol, ortga_kb("start", lang))
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
        send(chat_id, "Botdan foydalanish uchun kanalga obuna boling!", [[
            {"text": "Kanalga otish", "url": f"https://t.me/{CHANNEL[1:]}"},
            {"text": "Obuna boldim", "callback_data": "tekshir"}
        ]])
        return "ok"

    if text == "/start":
        save_user(user_id, ism)
        til_menyusi(chat_id)

    elif text == "/stats" and str(user_id) == ADMIN:
        send(chat_id, "Statistika Google Sheets da! docs.google.com/spreadsheets/d/1emuCXNa2pgs6LuzgNTiq1DYHLkzuQAXLhSHVgfiHoR0")

    elif text.startswith("/reklama ") and str(user_id) == ADMIN:
        msg = text[9:]
        send(chat_id, "Reklama yuborilmoqda...")

    else:
        if lang == "ru":
            send(chat_id, "Подготовка...")
        elif lang == "en":
            send(chat_id, "Preparing...")
        else:
            send(chat_id, "Tayyorlanmoqda...")
        role = get_role("savol", lang)
        if lang == "ru":
            role += " Отвечай на РУССКОМ языке."
        elif lang == "en":
            role += " Answer in ENGLISH."
        else:
            role += " Javobni OZBEKCHA yoz."
        javob = ask(text, role)
        if lang == "ru":
            kb = [[{"text": "Главное меню", "callback_data": "start"}]]
        elif lang == "en":
            kb = [[{"text": "Main menu", "callback_data": "start"}]]
        else:
            kb = [[{"text": "Bosh menyu", "callback_data": "start"}]]
        send(chat_id, javob, kb)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
