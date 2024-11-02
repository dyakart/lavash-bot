# обработчики событий, которые относятся к общению бота с пользователем в личке

from aiogram import F, types, Router
from aiogram.enums import ParseMode
# импортируем систему фильтрации сообщений и для работы с командами
from aiogram.filters import CommandStart, Command, or_f
# импортируем классы для форматирования текста
from aiogram.utils.formatting import as_list, as_marked_section, Bold
# для работы с асинхронными сессиями
from sqlalchemy.ext.asyncio import AsyncSession

# наши импорты
# импортируем фильтр для определения личка, группа, супергруппа
from filters.chat_types import ChatTypeFilter
# импортируем ответные клавиатуры
from kbds.reply import get_keyboard
# импортируем наши инлайн клавиатуры
from kbds.inline import get_callback_btns
# импортируем запросы для БД
from database.orm_query import orm_get_products

# создаем отдельный роутер для сообщений лички
user_private_router = Router()
# подключаем фильтр для определения, где будет работать роутер (в личке, в группе, супергруппе)
user_private_router.message.filter(ChatTypeFilter(['private']))


# обрабатываем команду /start
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    # отправляем стартовую клавиатуру пользователю
    await message.answer('Привет, я бот кафе «La-Ваш»',
                         reply_markup=get_keyboard(
                             'Меню:',
                             'О нас:',
                             'Варианты оплаты:',
                             'Варианты доставки:',
                             placeholder='Что Вас интересует?',
                             sizes=(2, 2)
                         ),
                         )


# обрабатываем команду /menu
# записываем команды, которые должны обрабатываться в Command
# @user_private_router.message(F.text.lower() == 'меню')
@user_private_router.message(or_f(Command('menu'), (F.text.lower() == 'меню')))
async def menu_cmd(message: types.Message, session: AsyncSession):
    # Получаем список товаров
    products = await orm_get_products(session)
    if not products:
        await message.answer("Список товаров пуст 🚫")
        return
    # Если список не пуст, выводим товары
    for product in products:
        await message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}\
                    </strong>\n{product.description}\nВес: {product.weight} гр.\nСтоимость: {round(product.price, 2)} ₽",
            reply_markup=get_callback_btns(btns={
                # текст: данные, которые хотим передать с этой кнопкой
                'Удалить': f'delete_{product.id}',
                'Изменить': f'change_{product.id}'
            })
        )
    await message.answer("❤️ ОК, вот меню ⏫")


# обрабатываем команду /about
@user_private_router.message(F.text.lower() == 'о нас')
@user_private_router.message(Command('about'))
async def menu_cmd(message: types.Message):
    await message.answer("О нас:")


# обрабатываем команду /payment
@user_private_router.message(F.text.lower() == 'варианты оплаты')
@user_private_router.message(Command('payment'))
async def menu_cmd(message: types.Message):
    # текст для ответа в виде маркированного списка, сначала идёт заголовок
    text = as_marked_section(
        Bold('Варианты оплаты:'),
        'Картой в боте',
        'При получении (карта / наличные)',
        marker='✅ '
    )
    # as_html() - обрабатываем наш ответ, как html текст
    await message.answer(text.as_html())


# обрабатываем команду /delivery
# F - магический фильтр, по которому будем фильтровать сообщения (указывается в конце, после других обработчиков)
@user_private_router.message((F.text.lower().contains('доставк')) | (F.text.lower() == 'варианты доставки'))
@user_private_router.message(Command('delivery'))
async def menu_cmd(message: types.Message):
    # текст для ответа в виде маркированных списков, сначала идёт заголовок
    text = as_list(
        as_marked_section(
            Bold('Варианты доставки заказа:'),
            'Курьер',
            'Самовывоз (сейчас приеду, заберу)',
            'Покушаю у Вас',
            marker='✅ '
        ),
        as_marked_section(
            Bold('Нельзя:'),
            'Почта',
            'Голуби',
            marker='❌ '
        ),
        # указываем разделитель секций
        sep='\n----------------------\n'
    )
    # as_html() - обрабатываем наш ответ, как html текст
    await message.answer(text.as_html())
