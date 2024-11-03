# обработчики событий, которые относятся к общению бота с пользователем в личке

from aiogram import F, types, Router
# импортируем систему фильтрации сообщений и для работы с командами
from aiogram.filters import CommandStart
# для работы с асинхронными сессиями
from sqlalchemy.ext.asyncio import AsyncSession

# наши импорты
# импортируем фильтр для определения личка, группа, супергруппа
from filters.chat_types import ChatTypeFilter
# импортируем наши инлайн клавиатуры
from kbds.inline import MenuCallBack, get_callback_btns
# импортируем запросы для БД
from database.orm_query import (
    orm_add_to_cart,
    orm_add_user,
)
# генератор меню
from handlers.menu_processing import get_menu_content

# создаем отдельный роутер для сообщений лички
user_private_router = Router()
# подключаем фильтр для определения, где будет работать роутер (в личке, в группе, супергруппе)
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    # при команде /start определяем уровень 0 и название меню - main (главная страница
    # media = image, kbds = reply_markup (from menu_processing.py)
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    if media is None:
        await message.answer("❌ Временно недоступно!")
        return

    # получаем изображение (media.media) и описание (media.caption) из объекта InputMediaPhoto
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)

    # await message.answer("Привет, я бот кафе «La-Ваш» ❤️",
    #                      reply_markup=get_callback_btns(btns={
    #                          'Нажми меня': 'some_1'
    #                      }))


async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    await orm_add_user(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer("✅ Товар добавлен в корзину!")


# любые callback, которые будут приходить от пользователя (нажатия на инлайн кнопки, например), и где
# есть префикс menu, будут обрабатываться здесь
@user_private_router.callback_query(MenuCallBack.filter())
# callback_data:MenuCallBack - чтобы получить строку из нужного callback
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    if callback_data.menu_name == "add_to_cart":
        await add_to_cart(callback, callback_data, session)
        return

    media, reply_markup = await get_menu_content(
        session,
        # заполняем атрибуты из класса MenuCallBack
        # уровень берём из callback строки
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )

    if isinstance(media, str):
        await callback.answer()
        # Если media - это строка, используем callback для отправки текста
        await callback.message.answer(media)
        return

    if media is None:
        await callback.answer()
        await callback.message.answer("❌ Временно недоступно!")
        return

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()
