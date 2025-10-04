Бесплатный бот переводчик для Телеграмма.
Он так же работает в ргупповых чатах.
Делал бота с помощью DeepSeek.
Код предназначен для хостинга https://railway.com/



Подготовка файлов проекта

Создай в папке проекта следующие файлы:

bot.py - основной файл бота

requirements.txt - зависимости (создай файл и вставь туда код ниже)

python-telegram-bot==21.7
deep-translator==1.11.4
python-dotenv==1.0.0

Procfile - инструкция для запуска (создай файл и вставь туда код ниже)

worker: python bot.py

.env - для локального тестирования (не загружается на Railway) (создай файл и вставь туда код ниже)

BOT_TOKEN=your_bot_token_here



Размещение на Railway



Шаг 1: Регистрация

    Перейди на railway.app

    Войди через GitHub

Шаг 2: Создание проекта

    Нажми "New Project"

    Выбери "Deploy from GitHub repo"

Шаг 3: Подключение репозитория

    Если код в GitHub - подключи репозиторий

    Если нет - создай репозиторий и загрузи код:

bash

git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/твой-username/твой-репозиторий.git
git push -u origin main

Шаг 4: Настройка переменных окружения

В проекте на Railway:

    Перейди в Settings → Variables

    Добавь переменную:

        Name: BOT_TOKEN

        Value: токен_твоего_бота (который получил от @BotFather)

Шаг 5: Деплой

    Railway автоматически запустит деплой при пуше в GitHub

    Или нажми "Deploy" вручную

4. Проверка работы

После деплоя:

    Проверь логи в Railway: View Logs

    Должна быть надпись: "🤖 Бот запущен на Railway!"

    Напиши боту в ЛС: /start

    Добавь бота в группу и протестируй

5. Важные моменты
Если бот не запускается:

    Проверь, что в Procfile указано worker: python bot.py

    Убедись, что переменная BOT_TOKEN установлена правильно

    Проверь логи в Railway

Для обновления бота:
bash

git add .
git commit -m "Update bot"
git push

6. Структура проекта на GitHub

Твой репозиторий должен содержать:
text

telegram-translator-bot/
├── bot.py
├── requirements.txt
├── runtime.txt
├── Procfile
└── README.md (опционально)
