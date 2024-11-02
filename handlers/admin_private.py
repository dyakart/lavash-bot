# админка

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
# импортируем машину состояний
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
# для работы с асинхронными сессиями
from sqlalchemy.ext.asyncio import AsyncSession

# наши импорты
from filters.chat_types import ChatTypeFilter, IsAdmin
# генератор обычных клавиатур
from kbds.reply import get_keyboard
# генератор inline клавиатур
from kbds.inline import get_callback_btns
# импортируем запросы для БД
from database.orm_query import (
    orm_add_product,
    orm_delete_product,
    orm_get_product,
    orm_get_products,
    orm_update_product
)

# создаём роутер для админки
admin_router = Router()
# подключаем фильтр для определения, где будет работать роутер (в личке, в группе, супергруппе), добавляем проверку
# является ли пользователь админом
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

# формируем клавиатуру для админки
ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Ассортимент",
    placeholder="Выберите действие",
    sizes=(2,),
)

# формируем клавиатуру для админки
BACK_KB = get_keyboard(
    "Назад",
    "Отмена",
    placeholder="Выберите действие",
    sizes=(1, 1),
)


# для добавления продукта
class AddProduct(StatesGroup):
    # перечисляем шаги (состояния, через которые будет проходить админ)
    # 1 шаг(состояние) - ввод имени
    name = State()
    # 2 шаг - ввод описания
    description = State()
    # 3 шаг - ввод веса продукта
    weight = State()
    # 4 шаг - ввод стоимости
    price = State()
    # 5 шаг - отправка фото
    image = State()

    # продукт, который изменяется
    product_for_change = None

    # словарь, в котором перечисляем, что будем отправлять пользователю на каждом шаге назад
    texts = {
        'AddProduct:name': 'Введите название заново\n❗ Если Вы изменяете товар, отправьте точку, чтобы оставить старое название',
        'AddProduct:description': 'Введите описание заново\n❗ Если Вы изменяете товар, отправьте точку, чтобы оставить старое описание',
        'AddProduct:weight': 'Введите вес заново\n❗ Если Вы изменяете товар, отправьте точку, чтобы оставить старый вес товара',
        'AddProduct:price': 'Введите стоимость заново\n❗ Если Вы изменяете товар, отправьте точку, чтобы оставить старую стоимость',
        'AddProduct:image': 'Это последний шаг..',
    }


# при новом запуске бота, нужно прописывать в группе команду /admin, чтобы все администраторы получили доступ к админке
@admin_router.message(Command("admin"))
async def add_product(message: types.Message):
    await message.answer("Что хотите сделать ❓", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Ассортимент")
async def starring_at_product(message: types.Message, session: AsyncSession):
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
    await message.answer("❤️ ОК, вот список товаров ⏫")


# инлайн удаление
# ловим текст из callback_query, который начинается на delete_
@admin_router.callback_query(F.data.startswith('delete_'))
# callback - наше название, для удобства
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    # удаляем delete_, оставляем только id продукта
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))

    # даем серверу телеграмм понять, что мы обработали кнопку удалить
    await callback.answer("✅ Товар удален")
    # отправляем в ответ на нажатие кнопки
    await callback.message.answer("✅ Товар удален!")


# инлайн изменение
# ловим текст из callback_query, который начинается на change_ и подключаем машину состояний
@admin_router.callback_query(StateFilter(None), F.data.startswith('change_'))
# callback - наше название, для удобства
async def change_product(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    # удаляем change_, оставляем только id продукта
    product_id = callback.data.split("_")[-1]
    # получаем продукт из БД
    product_for_change = await orm_get_product(session, int(product_id))

    AddProduct.product_for_change = product_for_change

    # даем серверу телеграмм понять, что мы обработали кнопку изменить
    await callback.answer()
    # отправляем в ответ на нажатие кнопки и удаляем клавиатуру
    await callback.message.answer(
        "Введите название товара\n❗ Если Вы изменяете товар, отправьте точку, чтобы оставить старое название",
        reply_markup=BACK_KB)
    # и переходим в состояние ввода названия продукта (далее мы пройдём все этапы, как при добавлении)
    await state.set_state(AddProduct.name)


# Код ниже для машины состояний (FSM)


# проверяем, что у пользователя нет активных состояний - StateFilter(None)
@admin_router.message(StateFilter(None), F.text == "Добавить товар")
# передаем FSMContext, чтобы контролировать состояния пользователя
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        # ждём название товара от админа, удаляем админ клавиатуру
        "Введите название товара\n❗ Если Вы изменяете товар, отправьте точку, чтобы оставить старое название",
        reply_markup=BACK_KB
    )
    # становимся в состояние ожидания (названия товара)
    await state.set_state(AddProduct.name)


# обработчик для отмены всех состояний
# добавляем StateFilter('*'), где '*' - любое состояние пользователя
@admin_router.message(StateFilter('*'), Command("отмена"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    # получаем текущее состояние
    current_state = await state.get_state()
    # если у пользователя нет ни одного состояния, то выходим из этого обработчика
    if current_state is None:
        return
    # если товар изменялся, а потом пользователь нажал отмена, обновляем значение product_for_change
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    # иначе очищаем все состояния у пользователя
    await state.clear()
    # пишем сообщение и возвращаем админ клавиатуру
    await message.answer("✅ Действия отменены", reply_markup=ADMIN_KB)


@admin_router.message(StateFilter('*'), Command("назад"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    # получаем текущее состояние
    current_state = await state.get_state()
    # если у пользователя состояние ввода названия товара
    if current_state == AddProduct.name:
        await message.answer(
            '🚫 Предыдущего шага нет!\nВведите название товара или нажмите/напишите "отмена" для выхода')
        # выходим из обработчика
        return

    # создаем переменную для предыдущего состояния
    previous = None
    # проходимся по всем нашим состояниям в AddProduct
    for step in AddProduct.__all_states__:
        # если полученное состояние = текущему состоянию
        if step.state == current_state:
            # устанавливаем значение предыдущего состояния
            await state.set_state(previous)
            await message.answer(f'👌, Вы вернулись к предыдущему шагу.\n{AddProduct.texts[previous.state]}')
            return
        # будет обновляться, пока не попадёт в условие, а когда попадет, то станет известно предыдущее состояние
        # например, состояние description не прошёл в условие, но следующее price - прошло, значит
        # предыдущее это состояние description
        previous = step


# если пользователь находится в состоянии ввода названия товара, то
# добавляем название и ждём описание товара от админа
@admin_router.message(AddProduct.name, or_f(F.text, F.text == "."))
async def add_name(message: types.Message, state: FSMContext):
    # если точка, то берём старое название у продукта, который хотим изменить
    if message.text == ".":
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        # дополнительная проверка, если больше, то выходим из обработчика не меняя состояния, отправляем сообщение
        if len(message.text) >= 100:
            await message.answer(
                "🚫 Название товара не должно превышать 100 символов.\nВведите название заново"
            )
            return
        # обновляем наши данные о товаре (название) из текста пользователя
        await state.update_data(name=message.text)
    await message.answer(
        "Введите описание товара\n❗ Если Вы изменяете товар, отправьте точку, чтобы оставить старое описание")
    # становимся в состояние ожидания (описание товара)
    await state.set_state(AddProduct.description)


# если пользователь ввёл то, что не соответствует фильтрации (например F.text), пишем об ошибке данных
@admin_router.message(AddProduct.name)
async def add_name(message: types.Message, state: FSMContext):
    await message.answer("🚫 Вы ввели недопустимые данные, введите текст названия товара!")


# если пользователь находится в состоянии ввода описания товара, то
# добавляем описание и ждём вес товара от админа
@admin_router.message(AddProduct.description, or_f(F.text, F.text == "."))
async def add_description(message: types.Message, state: FSMContext):
    # если точка, то берём старое описание у продукта, который хотим изменить
    if message.text == ".":
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        # обновляем наши данные о товаре (описание) из текста пользователя
        await state.update_data(description=message.text)
    await message.answer(
        "Введите вес товара\n❗ Если Вы изменяете товар, отправьте точку, чтобы оставить старый вес товара")
    # становимся в состояние ожидания (веса товара)
    await state.set_state(AddProduct.weight)


@admin_router.message(AddProduct.description)
async def add_description(message: types.Message, state: FSMContext):
    await message.answer("🚫 Вы ввели недопустимые данные, введите текст описания товара!")


# если пользователь находится в состоянии ввода веса товара, то
# добавляем вес и ждём стоимость товара от админа
@admin_router.message(AddProduct.weight, or_f(F.text, F.text == "."))
async def add_weight(message: types.Message, state: FSMContext):
    # если точка, то берём старый вес у продукта, который хотим изменить
    if message.text == ".":
        await state.update_data(weight=AddProduct.product_for_change.weight)
    else:
        try:
            int(message.text)
        except:
            await message.answer("🚫 Введите корректное значение веса товара (целое число)!")
            return
        # обновляем наши данные о товаре (стоимость) из текста пользователя
        await state.update_data(weight=message.text)
    # обновляем наши данные о товаре (вес) из текста пользователя
    await message.answer(
        "Введите стоимость товара\n❗ Если Вы изменяете товар, отправьте точку, чтобы оставить старую стоимость")
    # становимся в состояние ожидания (стоимости товара)
    await state.set_state(AddProduct.price)


@admin_router.message(AddProduct.weight)
async def add_weight(message: types.Message, state: FSMContext):
    await message.answer("🚫 Вы ввели недопустимые данные, введите вес товара в граммах!")


# если пользователь находится в состоянии ввода стоимости товара, то
# добавляем стоимость и ждём фото товара от админа
@admin_router.message(AddProduct.price, or_f(F.text, F.text == "."))
async def add_price(message: types.Message, state: FSMContext):
    # если точка, то берём старую цену у продукта, который хотим изменить
    if message.text == ".":
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except:
            await message.answer("🚫 Введите корректное значение цены!")
            return
        # обновляем наши данные о товаре (стоимость) из текста пользователя
        await state.update_data(price=message.text)

    await message.answer(
        "Загрузите изображение товара\n❗ Если Вы изменяете товар, отправьте точку, чтобы оставить старое фото")
    # становимся в состояние ожидания (фото товара)
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def add_price(message: types.Message, state: FSMContext):
    await message.answer("🚫 Вы ввели недопустимые данные, введите корректную стоимость товара!")


# если пользователь находится в состоянии отправки фото товара, то
# добавляем фото и возвращаем админ клавиатуру
@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    # если точка, то берём старое фото у продукта, который хотим изменить
    if message.text == ".":
        await state.update_data(image=AddProduct.product_for_change.image)
    else:
        # обновляем наши данные о товаре (фото) из файла пользователя
        # photo[-1] - это наше изображение с самым большим разрешением, file_id - получаем id фото
        await state.update_data(image=message.photo[-1].file_id)

    # формируем все полученные данные о товаре от админа (словарь)
    data = await state.get_data()
    try:
        # если мы изменяем продукт, то вызываем запрос update
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        # иначе добавляем продукт
        else:
            await orm_add_product(session, data)
        await message.answer("✅ Товар добавлен/изменен!", reply_markup=ADMIN_KB)
        # когда пользователь прошёл все пункты состояний, очищаем машину состояний пользователя
        await state.clear()
    except Exception as e:
        await message.answer(
            f"❌ Ошибка: \n{str(e)}\nОбратитесь к разработчику!", reply_markup=ADMIN_KB
        )
        await state.clear()
    # обновляем значение изменяемого продукта, после всех состояний
    AddProduct.product_for_change = None


@admin_router.message(AddProduct.image)
async def add_image(message: types.Message, state: FSMContext):
    await message.answer("🚫 Вы ввели недопустимые данные, отправьте фото товара!")
