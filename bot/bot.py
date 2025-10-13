import telebot
import requests
import json

# 🔑 Твой токен от BotFather
BOT_TOKEN = "7846522503:AAHTFBxR55dxNJA9omFZtqv9UXLFvTHcvE4"

# 🌐 URL к data.json на GitHub Pages
DATA_URL = "https://sisa6428.github.io/data.json"

bot = telebot.TeleBot(BOT_TOKEN)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Привет! 👋 Я бот проекта SiSA.\n"
        "Используй /price чтобы узнать текущую цену токена."
    )

# Команда /price — получает актуальную цену
@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        response = requests.get(DATA_URL)
        data = response.json()
        price = data.get("current_price")
        updated = data.get("last_updated", "неизвестно")

        bot.send_message(
            message.chat.id,
            f"💰 *Текущая цена:* {price} USD\n"
            f"🕒 *Последнее обновление:* {updated}",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка при получении данных: {e}")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
