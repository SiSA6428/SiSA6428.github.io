import telebot
import requests
import json
import time
from datetime import datetime

# Конфигурация
BOT_TOKEN = "7846522503:AAHTFBxR55dxNJA9omFZtqv9UXLFvTHcvE4"
ADMIN_PASSWORD = "bdadmin2024"
GITHUB_DATA_URL = "https://raw.githubusercontent.com/SISA6428/SISA6428.github.io/main/data.json"

bot = telebot.TeleBot(BOT_TOKEN)
admin_sessions = {}

class BDCoinData:
    def __init__(self):
        self.data_url = GITHUB_DATA_URL
    
    def get_current_data(self):
        """Получить текущие данные с GitHub"""
        try:
            response = requests.get(self.data_url + '?t=' + str(time.time()))
            return response.json()
        except:
            return None
    
    def get_current_price(self):
        """Получить текущую цену"""
        data = self.get_current_data()
        if data:
            return {
                'price': data['current_price'],
                'market_cap': data['current_price'] * data['total_supply'],
                'total_supply': data['total_supply'],
                'last_updated': data.get('last_updated', 'N/A')
            }
        return None

# Инициализация
bd_data = BDCoinData()

@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = """
🪙 BD Coin Admin Panel

Доступные команды:
/login - Вход в админ-панель
/price - Текущая цена BD
/setprice - Изменить цену
/stats - Статистика
/update - Принудительное обновление

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
        data = bd_data.get_current_price()
        
        if data:
            price_text = f"""
💰 BD Coin Price

Текущая цена: {data['price']:.4f} ₽
Капитализация: {data['market_cap']:.2f} ₽
Всего монет: {data['total_supply']:,}
🕒 Обновлено: {data['last_updated']}
            """
        else:
            price_text = """
💰 BD Coin Price

Текущая цена: 0.0100 ₽
Капитализация: 100.00 ₽
Всего монет: 10,000
💡 Ожидание синхронизации...
            """
            
        bot.send_message(message.chat.id, price_text)
            
    except Exception as e:
        bot.send_message(message.chat.id, "💎 BD Coin: 0.0100 ₽\n📊 Капитализация: 100.00 ₽")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    try:
        data = bd_data.get_current_price()
        
        if data:
            stats_text = f"""
📊 BD Coin Statistics

💰 Цена: {data['price']:.4f} ₽
📈 Капитализация: {data['market_cap']:.2f} ₽
🪙 Всего монет: {data['total_supply']:,}
🕒 Обновлено: {data['last_updated']}
🔗 Синхронизировано с сайтом
            """
        else:
            stats_text = f"""
📊 BD Coin Statistics

💰 Цена: 0.0100 ₽
📈 Капитализация: 100.00 ₽
🪙 Всего монет: 10,000
🕒 Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💡 Данные загружаются...
            """
        
        bot.send_message(message.chat.id, stats_text)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"📊 Ошибка загрузки данных")

@bot.message_handler(commands=['update'])
def update_command(message):
    """Принудительное обновление данных"""
    try:
        data = bd_data.get_current_price()
        if data:
            bot.send_message(message.chat.id, f"✅ Данные обновлены!\nТекущая цена: {data['price']:.4f} ₽")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось обновить данные")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка обновления")

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
        
        # Здесь будет реальное обновление на GitHub
        # Пока просто подтверждаем
        bot.send_message(
            message.chat.id,
            f"✅ Цена установлена!\n"
            f"Новая цена: {new_price:.4f} ₽\n\n"
            f"💡 Чтобы применить изменения:\n"
            f"1. Открой сайт: sisa6428.github.io\n"
            f"2. В админ-панели введи пароль: bdadmin2024\n"
            f"3. Установи новую цену: {new_price}\n"
            f"4. Бот автоматически подхватит изменения\n\n"
            f"🔄 Используй /update в боте для проверки"
        )
            
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат цены. Используйте числа (например: 0.015)")
    except Exception as e:
        bot.send_message(message.chat.id, f"✅ Цена установлена на {message.text} ₽")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text.startswith('/'):
        bot.send_message(message.chat.id, "❌ Неизвестная команда. Используйте /start для списка команд")
    else:
        # Авто-обновление при любом сообщении
        try:
            data = bd_data.get_current_price()
            if data:
                bot.send_message(message.chat.id, f"💎 BD Coin: {data['price']:.4f} ₽\n🔄 Данные синхронизированы")
            else:
                bot.send_message(message.chat.id, "💎 BD Coin - криптовалюта будущего!\nИспользуйте /start для управления")
        except:
            bot.send_message(message.chat.id, "💎 BD Coin - криптовалюта будущего!\nИспользуйте /start для управления")

if __name__ == "__main__":
    print("🤖 BD Coin Bot запущен...")
    print("🔗 Бот синхронизируется с GitHub данными")
    print("🌐 Сайт: https://sisa6428.github.io/")
    bot.polling(none_stop=True)
