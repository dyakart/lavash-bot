# ответы бота в виде клавиатуры

from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


# получаем данные для клавиатуры
def get_keyboard(
        # передаем текст кнопок
        *btns: str,
        # подсказку в поле ввода
        placeholder: str = None,
        # индекс кнопки номера телефона
        request_contact: int = None,
        # индекс кнопки локации
        request_location: int = None,
        # расположение кнопок на клавиатуре (например, (2,1) - две в первой строке, одна во второй и тд)
        sizes: tuple = (2,),
):
    """
    Параметры request_contact и request_location должны быть индексами btns нужных вам кнопок.
    Пример:📱🗺️
    get_keyboard(
        'Меню',
        'О магазине',
        'Варианты оплаты',
        'Варианты доставки',
        'Отправить номер телефона',
        placeholder='Что Вас интересует?',
        request_contact=4, (4 индекс нужной нам кнопки - Отправить номер телефона)
        sizes=(2,2,1)
    )
    """
    keyboard = ReplyKeyboardBuilder()

    # проходимся по кнопкам, которые получили (в примере их 5)
    for index, text in enumerate(btns, start=0):
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    # устанавливаем размер клавиатуры и подсказку для поля ввода
    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )
