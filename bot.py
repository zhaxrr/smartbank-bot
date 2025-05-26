import threading
import telebot
import sqlite3
from flask import Flask

# --- КОНФИГУРАЦИЯ ---
TOKEN = '7894937869:AAG9Oozid-KIQ9Yc0EYlAtABRuVGS36VoOw'
bot = telebot.TeleBot(TOKEN)
DB_PATH = 'database.db'

# --- НАСТРОЙКА БАЗЫ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER UNIQUE,
        dollar_alert INTEGER DEFAULT 0,
        netflix_alert INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def add_user(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (chat_id) VALUES (?)', (chat_id,))
    conn.commit()
    conn.close()

def update_user(chat_id, field, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f'UPDATE users SET {field}=? WHERE chat_id=?', (value, chat_id))
    conn.commit()
    conn.close()

def get_user(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE chat_id=?', (chat_id,))
    user = c.fetchone()
    conn.close()
    return user

# --- КОМАНДЫ БОТА ---
@bot.message_handler(commands=['start'])
def welcome(message):
    add_user(message.chat.id)
    bot.send_message(message.chat.id,
        "👋 Добро пожаловать в SmartBank Assistant!\n\n"
        "Доступные команды:\n"
        "/payment — Напоминание о платеже\n"
        "/amount — Посмотреть сумму платежа\n"
        "/optimize — Советы по экономии\n"
        "/suspicious — Подозрительная активность\n"
        "/dollar_alert — Уведомление при курсе $ > 500₸\n"
        "/netflix_reminder — Напоминание о Netflix\n"
        "/profile — Посмотреть настройки\n"
        "/check_dollar — Текущий курс доллара")

@bot.message_handler(commands=['payment'])
def notify_payment(message):
    bot.send_message(message.chat.id, "💳 Напоминаем: через 2 дня у вас платёж по кредиту. Хотите узнать сумму? /amount")

@bot.message_handler(commands=['amount'])
def show_amount(message):
    bot.send_message(message.chat.id, "💰 Сумма к оплате: 48,250₸")

@bot.message_handler(commands=['optimize'])
def optimize(message):
    bot.send_message(message.chat.id, "📊 Вы тратите 5,200₸ в месяц на подписки. Хотите сократить расходы?")

@bot.message_handler(commands=['suspicious'])
def suspicious(message):
    bot.send_message(message.chat.id, "⚠️ Обнаружена нестандартная операция на сумму 250,000₸. Подтвердите: /yes /no")

@bot.message_handler(commands=['yes', 'no'])
def confirm_activity(message):
    if message.text == '/yes':
        bot.send_message(message.chat.id, "✅ Спасибо. Операция подтверждена.")
    else:
        bot.send_message(message.chat.id, "🚫 Операция заблокирована. Мы свяжемся с вами.")

@bot.message_handler(commands=['dollar_alert'])
def subscribe_dollar(message):
    update_user(message.chat.id, 'dollar_alert', 1)
    bot.send_message(message.chat.id, "📈 Мы уведомим вас, если курс доллара превысит 500₸.")

@bot.message_handler(commands=['netflix_reminder'])
def subscribe_netflix(message):
    update_user(message.chat.id, 'netflix_alert', 1)
    bot.send_message(message.chat.id, "🎬 Напоминание о списании Netflix установлено!")

@bot.message_handler(commands=['profile'])
def profile(message):
    user = get_user(message.chat.id)
    if user:
        dollar_status = '✅' if user[2] else '❌'
        netflix_status = '✅' if user[3] else '❌'
        bot.send_message(message.chat.id,
            f"🧾 Ваши настройки:\n"
            f"- Уведомление по доллару: {dollar_status}\n"
            f"- Напоминание о Netflix: {netflix_status}")
    else:
        bot.send_message(message.chat.id, "Пользователь не найден. Пожалуйста, нажмите /start.")

@bot.message_handler(commands=['check_dollar'])
def check_dollar(message):
    bot.send_message(message.chat.id, "💵 Текущий курс доллара: 500.00₸")

# --- ЗАПУСК БОТА + FLASK ---
def run_bot():
    init_db()
    bot.polling(none_stop=True)

app = Flask(__name__)

@app.route('/')
def index():
    return "SmartBank Bot is running."

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
