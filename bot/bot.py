import telebot
import requests
import json
import time
import base64
from datetime import datetime

# КОНФИГУРАЦИЯ - ЗАПОЛНИ ЭТО!
BOT_TOKEN = "7846522503:AAHTFBxR55dxNJA9omFZtqv9UXLFvTHcvE4"
ADMIN_PASSWORD = "bdadmin2024"
GITHUB_TOKEN = "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"  # Нужно создать!
GITHUB_REPO = "SISA6428/SISA6428.github.io"
GITHUB_FILE_PATH = "data.json"

bot = telebot.TeleBot(BOT_TOKEN)
admin_sessions = {}

class GitHubManager:
    def __init__(self, token, repo, file_path):
        self.token = token
        self.repo = repo
        self.file_path = file_path
        self.api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_file_data(self):
        """Получить данные файла с GitHub"""
        try:
            response = requests.get(self.api_url, headers=self.headers)
            if response.status_code == 200:
                content = response.json()['content']
                content = base64.b64decode(content).decode('utf-8')
                return json.loads(content), response.json()['sha']
            return None, None
        except:
            return None, None
    
    def update_file(self, new_data):
        """Обновить файл на GitHub"""
        try:
            # Получаем текущие данные и SHA
            current_data, sha = self.get_file_data()
            if not current_data:
                return False
            
            # Обновляем цену
            current_data['current_price'] = new_data['current_price']
            current_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Добавляем в историю
            if 'price_history' not in current_data:
                current_data['price_history'] = []
            
            current_data['price_history'].append({
                'timestamp': int(time.time()),
                'price': new_data['current_price'],
                'date': datetime.now().strftime('%H:%M')
            })
            
            # Ограничиваем историю
            if len(current_data['price_history']) > 50:
                current_data['price_history'] = current_data['price_history'][-50:]
            
            # Кодируем обратно в base64
            content = json.dumps(current_data, indent=2, ensure_ascii=False)
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            # Отправляем на GitHub
            update_data = {
                "message": f"💰 Price update: {new_data['current_price']} RUB",
                "content": content_b64,
                "sha": sha
            }
            
            response = requests.put(self.api_url, headers=self.headers, json=update_data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error: {e}")
            return False

# Инициализация GitHub менеджера
github_mgr = GitHubManager(GITHUB_TOKEN, GITHUB_REPO, GITHUB_FILE_PATH)

class BDCoinData:
    def __init__(self):
        self.data_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_FILE_PATH}"
    
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
/update - Обновить данные

🔧 Бот МЕНЯЕТ цену на GitHub!
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
            price_text = "❌ Ошибка загрузки данных"
            
        bot.send_message(message.chat.id, price_text)
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

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
        
        # ОБНОВЛЯЕМ ЦЕНУ НА GITHUB!
        update_data = {
            'current_price': new_price
        }
        
        success = github_mgr.update_file(update_data)
        
        if success:
            bot.send_message(
                message.chat.id,
                f"✅ Цена ОБНОВЛЕНА на GitHub!\n"
                f"Новая цена: {new_price:.4f} ₽\n"
                f"🔄 Сайт автоматически подхватит изменения\n"
                f"🌐 sisa6428.github.io"
            )
        else:
            bot.send_message(message.chat.id, "❌ Ошибка обновления цены на GitHub")
            
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат цены")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['update'])
def update_command(message):
    """Обновить данные"""
    try:
        data = bd_data.get_current_price()
        if data:
            bot.send_message(message.chat.id, f"✅ Данные обновлены!\nЦена: {data['price']:.4f} ₽")
        else:
            bot.send_message(message.chat.id, "❌ Ошибка загрузки данных")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🤖 BD Coin Bot запущен...")
    print("🔗 Бот МЕНЯЕТ данные на GitHub!")
    bot.polling(none_stop=True)
