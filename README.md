# Lavash Bot

Lavash Bot — это Telegram-бот, созданный с использованием библиотеки Aiogram для кафе La-Ваш

## Содержание

- [Обзор проекта](#обзор-проекта)
- [Установка](#установка)
- [Использование](#использование)

## Обзор проекта

Бот кафе «La-Ваш» ❤️ Поможет сделать заказ и просмотреть меню 😋

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/dyakart/lavash-bot.git
   ```
2. Перейдите в директорию проекта:
   ```bash
   cd lavash-bot
   ```
3. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate   # для Windows: venv\Scripts\activate
   ```
4. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5. Добавьте в файл .env ваш Telegram Bot Token и строку подключения PostgreSQL:
   ```env
   TOKEN_TG=your_telegram_bot_token
   DB_URL=postgresql+asyncpg://login:passwd@localhost:5432/db_name
   ```
6. Запустите бота:
   ```bash
   python app.py
   ```

## Использование
После запуска бота можете отправлять ему команды, воспользовавшись клавиатурой бота.
