import telebot
import requests
from telebot import types

# 🔑 Вставь сюда свой токен
BOT_TOKEN = "7846522503:AAHTFBxR55dxNJA9omFZtqv9UXLFvTHcvE4"
bot = telebot.TeleBot(BOT_TOKEN)

# 🌐 URL до твоего JSON-файла на GitHub Pages
DATA_URL = "https://sisa6428.github.io/data.json"


def get_data():
    """Загружает актуальные данные о монете с сайта"""
    try:
        response = requests.get(DATA_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я BD Coin Bot.\n"
        "Используй команду /price чтобы узнать текущую цену."
    )


@bot.message_handler(commands=['price'])
def send_price(message):
    data = get_data()
    if not data:
        bot.send_message(message.chat.id, "⚠️ Не удалось получить данные о цене.")
        return

    price = data["current_price"]
    supply = data["total_supply"]
    capitalization = round(price * supply, 2)
    updated = data["last_updated"]

    text = (
        "💰 <b>BD Coin</b>\n"
        f"💵 Текущая цена: {price:.4f} ₽\n"
        f"🏦 Капитализация: {capitalization:.2f} ₽\n"
        f"🪙 Всего монет: {supply:,}\n"
        f"⏰ Обновлено: {updated}"
    )

    bot.send_message(message.chat.id, text, parse_mode="HTML")


print("🤖 Бот запущен и ждёт команды /price ...")
bot.polling(none_stop=True)
