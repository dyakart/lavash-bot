from aiogram.utils.formatting import Bold, as_list, as_marked_section


categories = ['Еда', 'Напитки']

# описание для баннеров
description_for_info_pages = {
    "main": "Добро пожаловать!",
    "about": "Кафе La-Ваш ❤️\nРежим работы - с 11:00 до 21:00",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        marker="✅ ",
    ).as_html(),
    "shipping": as_list(
        as_marked_section(
            Bold("Варианты доставки/заказа:"),
            "Самовывоз (сейчас прибегу заберу)",
            marker="✅ ",
        ),
        as_marked_section(Bold("Нельзя:"), "Почта", "Голуби", marker="❌ "),
        sep="\n----------------------\n",
    ).as_html(),
    'catalog': 'Категории:',
    'cart': '🚫🛒 В корзине ничего нет!'
}

