# точка входа

import asyncio
import os
from aiogram import Bot, Dispatcher, types
# импортируем класс для форматирования текста
from aiogram.enums import ParseMode
# импортируем класс для настроек бота
from aiogram.client.default import DefaultBotProperties

# библиотеки для автоматического нахождения нашего файла dotenv и его загрузки
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# наши импорты
# импортируем наш роутер для обработки событий в личке
from handlers.user_private import user_private_router
# импортируем наш роутер для обработки событий в группе
from handlers.user_group import user_group_router
# импортируем наш роутер для администрирования
from handlers.admin_private import admin_router
# импортируем функции для работы с БД
from database.engine import create_db, drop_db, session_maker
# импортируем наш промежуточный слой для сессий БД
from middlewares.db import DataBaseSession

# импортируем наши команды для бота (private - для личных сообщений)
from common.bot_cmds_list import private

# инициализируем класс бота, передаем токен
bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# добавляем список id наших администраторов
bot.my_admins_list = []

# создаем класс диспетчера, который отвечает за фильтрацию разных сообщений (сообщения от сервера telegram)
dp = Dispatcher()

# подключаем наши роутеры (работают в том же порядке)
dp.include_routers(user_private_router, user_group_router, admin_router)


# функция старта
async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()
    # если таблицы в БД существуют, то эта функция не выполнится
    await create_db()


# функция выключения
async def on_shutdown(bot):
    print('бот лег ;(')


# запуск бота
async def main():
    # запускаем функцию on_startup при запуске
    dp.startup.register(on_startup)
    # запускаем функцию on_shutdown при выключении
    dp.shutdown.register(on_shutdown)

    # вешаем на событие обновления промежуточный слой (после прохождения фильтров)
    # регистрируем сессию для каждого обработчика
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    # отвечаем только, когда бот онлайн
    await bot.delete_webhook(drop_pending_updates=True)
    # удалить все наши команды для лички
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    # отправляем все наши команды, которые будут у бота (только в личке)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    # слушаем сервер telegram и постоянно спрашиваем его про наличие каких-то изменений
    # resolve_used_update_types - все изменения, которые мы используем будут отслеживаться у сервера telegram
    # например, ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']
    # можно добавить skip_events: 'edited_message' - пример, чтобы временно ограничить какие-то события
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


# запускаем нашу функцию main
asyncio.run(main())
