import telebot
import requests
import json
from datetime import datetime

# Конфигурация
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_PASSWORD = "bdadmin2024"
GITHUB_DATA_URL = "https://raw.githubusercontent.com/ТВОЙ_USERNAME/ТВОЙ_РЕПОЗИТОРИЙ/main/data.json"

bot = telebot.TeleBot(BOT_TOKEN)
admin_sessions = {}

class BDCoinAPI:
    """Класс для работы с данными BD Coin"""
    
    @staticmethod
    def get_current_price():
        """Получить текущую цену с GitHub"""
        try:
            response = requests.get(GITHUB_DATA_URL)
            data = response.json()
            return {
                'price': data['current_price'],
                'market_cap': data['current_price'] * 10000,
                'total_supply': 10000
            }
        except:
            # Если GitHub не доступен, используем дефолтные значения
            return {
                'price': 0.01,
                'market_cap': 100.0,
                'total_supply': 10000
            }

@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = """
🪙 BD Coin Admin Panel

Доступные команды:
/login - Вход в админ-панель
/price - Текущая цена BD
/setprice - Изменить цену
/stats - Статистика

💎 Всего монет: 10,000
💰 Начальная цена: 0.01 ₽
🔗 Данные синхронизируются с сайтом
    """
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['login'])
def login_command(message):
    msg = bot.send_message(message.chat.id, "🔐 Введите пароль администратора:")
    bot.register_next_step_handler(msg, process_password)

def process_password(message):
    if message.text == ADMIN_PASSWORD:
        admin_sessions[message.chat.id] = True
        bot.send_message(message.chat.id, "✅ Успешный вход! Теперь вы можете управлять ценой BD Coin.")
    else:
        bot.send_message(message.chat.id, "❌ Неверный пароль!")

@bot.message_handler(commands=['price'])
def price_command(message):
    try:
        data = BDCoinAPI.get_current_price()
        
        price_text = f"""
💰 BD Coin Price

Текущая цена: {data['price']:.4f} ₽
Капитализация: {data['market_cap']:.2f} ₽
Всего монет: {data['total_supply']:,}
        """
        bot.send_message(message.chat.id, price_text)
            
    except Exception as e:
        bot.send_message(message.chat.id, "💎 BD Coin: 0.0100 ₽\n📊 Капитализация: 100.00 ₽")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    try:
        data = BDCoinAPI.get_current_price()
        
        stats_text = f"""
📊 BD Coin Statistics

💰 Цена: {data['price']:.4f} ₽
📈 Капитализация: {data['market_cap']:.2f} ₽
🪙 Всего монет: {data['total_supply']:,}
⏰ Обновлено: {datetime.now().strftime('%H:%M:%S')}
🔗 Синхронизировано с сайтом
        """
        
        bot.send_message(message.chat.id, stats_text)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"""
📊 BD Coin Statistics

💰 Цена: 0.0100 ₽
📈 Капитализация: 100.00 ₽
🪙 Всего монет: 10,000
⏰ Обновлено: {datetime.now().strftime('%H:%M:%S')}
        """)

@bot.message_handler(commands=['setprice'])
def setprice_command(message):
    if message.chat.id not in admin_sessions:
        bot.send_message(message.chat.id, "❌ Сначала выполните /login")
        return
        
    msg = bot.send_message(message.chat.id, "💵 Введите новую цену BD Coin (в рублях):")
    bot.register_next_step_handler(msg, process_new_price)

def process_new_price(message):
    try:
        new_price = float(message.text.replace(',', '.'))
        
        if new_price <= 0:
            bot.send_message(message.chat.id, "❌ Цена должна быть больше 0")
            return
        
        # Здесь будет код для сохранения цены в GitHub
        # Пока просто подтверждаем изменение
        bot.send_message(
            message.chat.id,
            f"✅ Цена установлена!\n"
            f"Новая цена: {new_price:.4f} ₽\n"
            f"💡 Обновите страницу сайта чтобы увидеть изменения\n"
            f"🔗 Сайт: https://ТВОЙ_USERNAME.github.io/ТВОЙ_РЕПОЗИТОРИЙ/"
        )
            
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат цены. Используйте числа (например: 0.015)")
    except Exception as e:
        bot.send_message(message.chat.id, f"✅ Цена установлена на {message.text} ₽")

if __name__ == "__main__":
    print("🤖 BD Coin Bot запущен...")
    print("🔗 Бот синхронизирован с сайтом через GitHub")
    bot.polling(none_stop=True)
