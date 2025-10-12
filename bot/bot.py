import telebot
import requests
import json
import time
from datetime import datetime

# КОНФИГУРАЦИЯ
BOT_TOKEN = "7846522503:AAHTFBxR55dxNJA9omFZtqv9UXLFvTHcvE4"
GITHUB_DATA_URL = "https://raw.githubusercontent.com/SISA6428/SISA6428.github.io/main/data.json"

bot = telebot.TeleBot(BOT_TOKEN)

class BDCoinData:
    def __init__(self):
        self.data_url = GITHUB_DATA_URL
    
    def get_current_data(self):
        """Получить текущие данные с GitHub"""
        try:
            # Добавляем случайное число чтобы избежать кеширования
            response = requests.get(self.data_url + '?t=' + str(time.time()))
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def get_current_price(self):
        """Получить текущую цену"""
        data = self.get_current_data()
        if data:
            return {
                'price': data.get('current_price', 0.01),
                'market_cap': data.get('current_price', 0.01) * data.get('total_supply', 10000),
                'total_supply': data.get('total_supply', 10000),
                'last_updated': data.get('last_updated', 'N/A')
            }
        else:
            # Возвращаем данные по умолчанию если не удалось загрузить
            return {
                'price': 0.01,
                'market_cap': 100.00,
                'total_supply': 10000,
                'last_updated': 'Не доступно'
            }

# Инициализация
bd_data = BDCoinData()

@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = """
🪙 BD Coin - Official Bot

Доступные команды:
/price - Текущая цена BD Coin
/stats - Статистика монеты
/info - Информация о проекте

💎 Всего монет: 10,000
💰 Текущая цена обновляется с сайта
🌐 Сайт: sisa6428.github.io
    """
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['price'])
def price_command(message):
    """Текущая цена BD Coin"""
    try:
        data = bd_data.get_current_price()
        
        price_text = f"""
💰 BD Coin Price

Текущая цена: {data['price']:.4f} ₽
Капитализация: {data['market_cap']:.2f} ₽
Всего монет: {data['total_supply']:,}
🕒 Данные с сайта: {data['last_updated']}

💡 Чтобы изменить цену:
1. Открой сайт: sisa6428.github.io
2. Введи пароль: bdadmin2024
3. Установи новую цену
        """
        bot.send_message(message.chat.id, price_text)
        
    except Exception as e:
        bot.send_message(message.chat.id, "💎 BD Coin: 0.0100 ₽\n📊 Капитализация: 100.00 ₽")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Статистика BD Coin"""
    try:
        data = bd_data.get_current_price()
        
        stats_text = f"""
📊 BD Coin Statistics

💰 Текущая цена: {data['price']:.4f} ₽
📈 Рыночная капитализация: {data['market_cap']:.2f} ₽
🪙 Всего монет: {data['total_supply']:,}
🕒 Обновлено: {data['last_updated']}
🔗 Источник: GitHub репозиторий

🌐 Управление ценой на сайте:
sisa6428.github.io
        """
        bot.send_message(message.chat.id, stats_text)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"""
📊 BD Coin Statistics

💰 Цена: 0.0100 ₽
📈 Капитализация: 100.00 ₽
🪙 Всего монет: 10,000
🔗 Обновите через несколько секунд
        """)

@bot.message_handler(commands=['info'])
def info_command(message):
    """Информация о проекте"""
    info_text = """
💎 BD Coin Project

Официальная криптовалюта BD Coin

📊 Характеристики:
• Всего монет: 10,000 BD
• Начальная цена: 0.01 ₽
• Темно-зеленый дизайн
• Real-time график цен

🌐 Веб-сайт:
sisa6428.github.io

🔧 Технологии:
• Frontend: HTML5, CSS3, JavaScript
• Charts: Chart.js
• Data: GitHub API
• Backend: JavaScript

📈 Управление:
Цена обновляется через веб-интерфейс
и автоматически синхронизируется с ботом
        """
    bot.send_message(message.chat.id, info_text)

@bot.message_handler(commands=['refresh'])
def refresh_command(message):
    """Принудительное обновление данных"""
    try:
        data = bd_data.get_current_price()
        bot.send_message(message.chat.id, f"✅ Данные обновлены!\nТекущая цена: {data['price']:.4f} ₽")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка обновления")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Обработка всех сообщений"""
    if message.text.startswith('/'):
        bot.send_message(message.chat.id, "❌ Неизвестная команда. Используйте /start")
    else:
        # Показываем текущую цену при любом сообщении
        try:
            data = bd_data.get_current_price()
            bot.send_message(message.chat.id, f"💎 BD Coin: {data['price']:.4f} ₽\n📊 Кап: {data['market_cap']:.2f} ₽")
        except:
            bot.send_message(message.chat.id, "💎 BD Coin - криптовалюта будущего! 🚀")

if __name__ == "__main__":
    print("🤖 BD Coin Bot запущен...")
    print("🔗 Бот читает данные с GitHub")
    print("🌐 Сайт: https://sisa6428.github.io")
    bot.polling(none_stop=True)
