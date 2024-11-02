# обработчики событий, которые относятся к общению бота в группе

# импортируем библиотеку для запрета обхода запрещенных слов с помощью пунктуации
from string import punctuation
# импортируем запретные русские слова
from badwords_r import badwrds

from aiogram import F, Bot, types, Router
# импортируем класс для работы с командами
from aiogram.filters import Command
# импортируем фильтр для определения личка, группа, супергруппа
from filters.chat_types import ChatTypeFilter

user_group_router = Router()
# подключаем фильтр для определения, где будет работать роутер (в личке, в группе, супергруппе)
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))
user_group_router.edited_message.filter(ChatTypeFilter(['group', 'supergroup']))


# обработчик для команды /admin
@user_group_router.message(Command("admin"))
async def get_admins(message: types.Message, bot: Bot):
    # получаем id беседы, из которой была отправлена данная команда
    chat_id = message.chat.id
    # получаем список администраторов этой беседы (объекты в виде словаря)
    admins_list = await bot.get_chat_administrators(chat_id)

    # просмотреть все данные и свойства полученных объектов
    # print(admins_list)

    # формируем список id администраторов / создателя беседы
    admins_list = [
        # заносим id пользователя в этот список
        member.user.id
        # перебираем полученный список администраторов
        for member in admins_list
        # если статус пользователя creator или administrator
        if member.status == "creator" or member.status == "administrator"
    ]
    # передаём в атрибут полученный список id
    bot.my_admins_list = admins_list
    # и удалим эту команду из чата, если её написал пользователь из списка администраторов
    if message.from_user.id in admins_list:
        await message.delete()
    # print(admins_list)


# вырезаем все знаки пунктуации из текста, чтобы точнее проверить его на запретные слова
def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


# обработчик на любое измененное сообщение
@user_group_router.edited_message()
# обработчик на любое отправленное сообщение
@user_group_router.message()
async def cleaner(message: types.Message):
    # очищаем текст сообщения от знаков пунктуации и приводим к нижнему регистру
    clean_text_message = clean_text(message.text.lower())
    # если есть запрещенные слова в сообщении пользователя
    if any(badword in clean_text_message for badword in badwrds):
        # отправляем сообщение, чтобы соблюдался порядок
        await message.answer(f'{message.from_user.first_name}, соблюдайте порядок в чате!')
        # удаляем это сообщение
        await message.delete()
        # баним пользователя, который отправил это сообщение
        # await message.chat.ban(message.from_user.id)
