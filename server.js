const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Хранилище данных
const chats = new Map(); // code -> {messages: [], users: []}
const usedCodes = new Set();

// Генерация случайного кода
function generateCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
}

// Middleware
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// Маршруты
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Socket.io соединения
io.on('connection', (socket) => {
    console.log('Новое подключение:', socket.id);

    // Создание нового чата
    socket.on('create_chat', () => {
        let code;
        do {
            code = generateCode();
        } while (usedCodes.has(code));
        
        usedCodes.add(code);
        chats.set(code, {
            messages: [],
            users: [socket.id],
            created: Date.now()
        });

        socket.join(code);
        socket.emit('chat_created', code);
        console.log(`Создан чат с кодом: ${code}`);
    });

    // Присоединение к чату
    socket.on('join_chat', (code) => {
        code = code.toUpperCase();
        
        if (!chats.has(code)) {
            socket.emit('error', 'Чат не найден');
            return;
        }

        const chat = chats.get(code);
        if (!chat.users.includes(socket.id)) {
            chat.users.push(socket.id);
        }

        socket.join(code);
        socket.emit('join_success', {
            code: code,
            messages: chat.messages
        });

        // Уведомляем других участников
        socket.to(code).emit('user_joined', `Новый участник присоединился`);
        
        console.log(`Пользователь присоединился к чату: ${code}`);
    });

    // Отправка сообщения
    socket.on('send_message', (data) => {
        const { code, message, username } = data;
        
        if (!chats.has(code)) {
            socket.emit('error', 'Чат не найден');
            return;
        }

        const chat = chats.get(code);
        const messageData = {
            id: Date.now() + Math.random(),
            text: message,
            username: username || 'Аноним',
            timestamp: new Date().toLocaleTimeString(),
            socketId: socket.id
        };

        chat.messages.push(messageData);
        
        // Сохраняем только последние 100 сообщений
        if (chat.messages.length > 100) {
            chat.messages = chat.messages.slice(-100);
        }

        // Отправляем сообщение всем в чате
        io.to(code).emit('new_message', messageData);
    });

    // Обработка отключения
    socket.on('disconnect', () => {
        console.log('Пользователь отключен:', socket.id);
        
        // Удаляем пользователя из всех чатов
        chats.forEach((chat, code) => {
            chat.users = chat.users.filter(userId => userId !== socket.id);
            
            // Если чат пустой, удаляем его через 1 час
            if (chat.users.length === 0) {
                setTimeout(() => {
                    if (chats.has(code) && chats.get(code).users.length === 0) {
                        chats.delete(code);
                        usedCodes.delete(code);
                        console.log(`Чат ${code} удален`);
                    }
                }, 3600000); // 1 час
            }
        });
    });
});

// Очистка старых чатов каждые 10 минут
setInterval(() => {
    const now = Date.now();
    const hourAgo = now - 3600000; // 1 час назад
    
    chats.forEach((chat, code) => {
        if (chat.created < hourAgo && chat.users.length === 0) {
            chats.delete(code);
            usedCodes.delete(code);
            console.log(`Удален старый чат: ${code}`);
        }
    });
}, 600000); // 10 минут

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`🚀 Сервер запущен на порту ${PORT}`);
    console.log(`📱 Откройте http://localhost:${PORT} в браузере`);
});
