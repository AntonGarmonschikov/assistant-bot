import logging

from aiogram import Bot, Dispatcher, types
import ast
import os

from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get('TOKEN')
chat_id = os.environ.get('CHAT_ID')

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def open_file():
    """
    Функция извлечения словаря из файла
    :return: словарь с данными. Если файла не существует, возвращает пустой словарь.
    """
    try:
        with open('data.txt', 'r') as file:
            data = file.read()
            data_dict = ast.literal_eval(data)
            return data_dict
    except FileNotFoundError:
        return dict()


def message_lists():
    """
    Функция формирует сообщение о содержании списков
    :return: str
    """

    data_dict = open_file()

    if 'staff' not in data_dict:
        m_staff_list = 'Список пуст'
    else:
        m_staff_list = ", ".join(data_dict["staff"])

    if 'objects' not in data_dict:
        m_objects_list = 'Список пуст'
    else:
        m_objects_list = ", ".join(data_dict["objects"])

    return m_staff_list, m_objects_list


def add_data(user_message: types.Message, key: str) -> None:
    """
    Функция добавления данных в список
    :param user_message: сообщение пользователя
    :param key: ключ словаря к которому привязан соответствующий список
    :return: None
    """

    user_data_list = user_message.text.split(', ')

    data_dict = open_file()

    for i_element in user_data_list:
        try:
            data_dict[key].append(i_element.title())
        except KeyError:
            data_dict[key] = [i_element.title()]

    with open('data.txt', 'w') as file:
        file.write(str(data_dict))


def delete_data(user_message: types.Message, key: str):
    """
    Функция удаления данных из списка
    :param user_message: сообщение пользователя
    :param key: ключ словаря к которому привязан соответствующий список
    :return: в случае отсутствия данных в списке, возвращает str
    """
    try:
        if ',' not in user_message.text:
            user_data_list = user_message.text.split(', ')
        else:
            user_data_list = user_message.text.split(', ')

        data_dict = open_file()

        if len(user_data_list) != len(data_dict[key]):
            for i_element in user_data_list:
                data_dict[key].remove(i_element.title())
        else:
            data_dict.pop(key)

        with open('data.txt', 'w') as file:
            file.write(str(data_dict))

    except ValueError:
        return 'error'


def get_keyboard(data_dict: dict, key: str) -> list:
    """
    Функция формирования inline-кнопок из списка
    :param data_dict: словарь с данными
    :param key: ключ словаря к которому привязан соответствующий список
    :return: возвращает по 2 кнопки в каждой строке
    """
    buttons = [types.InlineKeyboardButton(text=f'{i_element}', callback_data=f'{i_element}') for i_element in
               data_dict[key]]

    for i in range(0, len(buttons), 2):
        yield buttons[i: i + 2]


# Хэндлер на команду /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user_channel_status = await bot.get_chat_member(chat_id=chat_id, user_id=message.chat.id)

    # фильтрация пользователей
    if user_channel_status['status'] in ['creator', 'administrator']:

        kb = [
            [
                types.KeyboardButton(text="📁Списки"),
                types.KeyboardButton(text="🚐Выезды")
            ]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            f"Здравствуйте, {user_channel_status['user']['first_name']}👋. Меня зовут Маргарита Степановна. Я ваш личный ассистент-бот.",
            reply_markup=keyboard)
    else:
        await message.answer("Доступ закрыт")


# Хэндлер на команду /help
@dp.message_handler(commands=['help'])
async def process_start_command(message: types.Message):
    user_channel_status = await bot.get_chat_member(chat_id=chat_id, user_id=message.chat.id)
    if user_channel_status['status'] in ['creator', 'administrator']:
        await message.answer("Редактирование списков садовников и объектов осуществляется при нажатии кнопки 'Списки'.\n\n"
                             "Для отправки информации о предстоящих выездах в группу осуществляется через кнопку 'Выезды'.\n\n"
                             "Во время формирования информации следует действовать согласно появляющимся сообщениям. "
                             "Сбор информации осуществляется по кнопкам, за исключениям, даты, времени и дополнительной информации. "
                             "После ввода даты, времени и дополнительной информации необходимо нажать значок меню кнопок (пуговица) и выбрать необходимую кнопку. "
                             "По завершению выбора сотрудников и объектов для сформирования списков необходимо нажать кнопку 'Подтвердить'. \n\n"
                             "Доп. информация (необязательно) - содержит необходимую информацию сотрудникам для выполнения поставленных задач на объектах.")

    else:
        await message.answer("Доступ закрыт")


# Хэндлер на команду /списки
@dp.message_handler(text=["📁Списки"])
async def lists(message: types.Message):
    staff_list, objects_list = message_lists()

    await message.answer(f"Сотрудники 🧑‍🌾:\n{staff_list}\n\n"
                         f"Объекты 🏠:\n{objects_list}")

    kb = [
        [
            types.KeyboardButton(text="Сотрудники🧑‍🌾"),
            types.KeyboardButton(text="Объекты🏠")
        ],
        [
            types.KeyboardButton(text="↩Меню")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выберите список ⬇", reply_markup=keyboard)


# Хэндлер на команду /Сотрудники
@dp.message_handler(text=["Сотрудники🧑‍🌾"])
async def staff(message: types.Message, state: FSMContext):
    # сохранение ключа для словаря с данными, уникальных фраз для информационного сообщения
    async with state.proxy() as data:
        data['key'] = 'staff'
        data['unique_string_1'] = 'имя сотрудника которого'
        data['unique_string_2'] = 'сотрудник'

    kb = [
        [
            types.KeyboardButton(text="Добавить"),
            types.KeyboardButton(text="Удалить")
        ],
        [
            types.KeyboardButton(text="Назад")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выберите действие ⬇", reply_markup=keyboard)


# Хэндлер на команду /Объекты
@dp.message_handler(text=["Объекты🏠"])
async def objects(message: types.Message, state: FSMContext):
    # сохранение ключа для словаря с данными, уникальных фраз для информационного сообщения
    async with state.proxy() as data:
        data['key'] = 'objects'
        data['unique_string_1'] = 'название объекта который'
        data['unique_string_2'] = 'объект'

    kb = [
        [
            types.KeyboardButton(text="Добавить"),
            types.KeyboardButton(text="Удалить")
        ],
        [
            types.KeyboardButton(text="Назад")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выберите действие ⬇", reply_markup=keyboard)


# Хэндлер на команду /Назад
@dp.message_handler(text=["Назад"])
async def back(message: types.Message, state: FSMContext):
    kb = [
        [
            types.KeyboardButton(text="Сотрудники🧑‍🌾"),
            types.KeyboardButton(text="Объекты🏠")
        ],
        [
            types.KeyboardButton(text="↩Меню")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выберите список ⬇", reply_markup=keyboard)

    await state.finish()


# Хэндлер на команду /Меню
@dp.message_handler(text=["↩Меню"])
async def menu(message: types.Message, state: FSMContext):
    kb = [
        [
            types.KeyboardButton(text="📁Списки"),
            types.KeyboardButton(text="🚐Выезды")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Главное меню", reply_markup=keyboard)

    await state.finish()


# Хэндлер на команду /Добавить, /Удалить
@dp.message_handler(text=["Добавить", "Удалить"])
async def add_delete_data(message: types.Message, state: FSMContext):
    # сохранение название команды, выгрузка уникальных фраз для информационного сообщения
    async with state.proxy() as data:
        data['action'] = message.text

        unique_string_1 = data['unique_string_1']
        unique_string_2 = data['unique_string_2']

    await message.answer(f'Введите {unique_string_1} хотите {message.text.lower()}. '
                         f'Если {unique_string_2} не один, введите их через запятую:')


# Хэндлер на команду /Выезды
@dp.message_handler(text=["🚐Выезды"])
async def update_num_text(message: types.Message):
    staff_list, objects_list = message_lists()

    if staff_list == 'Список пуст':
        kb = [
            [
                types.KeyboardButton(text="📁Списки"),
                types.KeyboardButton(text="🚐Выезды")
            ]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Список сотрудников пуст.", reply_markup=keyboard)

    elif objects_list == 'Список пуст':
        kb = [
            [
                types.KeyboardButton(text="📁Списки"),
                types.KeyboardButton(text="🚐Выезды")
            ]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Список объектов пуст", reply_markup=keyboard)

    else:
        kb = [
            [
                types.KeyboardButton(text="📆Дата"),
                types.KeyboardButton(text="↩Меню")
            ]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Выберите действие ⬇", reply_markup=keyboard)


# Хэндлер на команду /Дата
@dp.message_handler(text=["📆Дата"])
async def update_num_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['action'] = 'date'

    kb = [
        [
            types.KeyboardButton(text="🧑‍🌾Сотрудники"),
            types.KeyboardButton(text="↩Меню")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer('Введите дату выезда на объект:', reply_markup=keyboard)


# Хэндлер на команду /Сотрудники (при формировании сообщения о выезде)
@dp.message_handler(text=["🧑‍🌾Сотрудники"])
async def staff_list(message: types.Message, state: FSMContext):
    kb = [
        [
            types.KeyboardButton(text="🏠Объекты"),
            types.KeyboardButton(text="↩Меню")
        ]
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выбор сотрудников", reply_markup=keyboard)

    data_dict = open_file()

    buttons = get_keyboard(data_dict, 'staff')

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    keyboard.add(types.InlineKeyboardButton(text='Подтвердить', callback_data='finish'))

    await message.answer('Сотрудники:', reply_markup=keyboard)

    async with state.proxy() as data:
        data['key'] = 'staff'


# Хэндлер на команду /Объекты (при формировании сообщения о выезде)
@dp.message_handler(text=["🏠Объекты"])
async def object_list(message: types.Message, state: FSMContext):
    kb = [
        [
            types.KeyboardButton(text="🕗Время"),
            types.KeyboardButton(text="↩Меню")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выбор объекта", reply_markup=keyboard)

    data_dict = open_file()

    buttons = get_keyboard(data_dict, 'objects')

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    keyboard.add(types.InlineKeyboardButton(text='Подтвердить', callback_data='finish'))

    await message.answer('Объекты:', reply_markup=keyboard)

    async with state.proxy() as data:
        data['key'] = 'objects'


# Хэндлер на команду /Время
@dp.message_handler(text=["🕗Время"])
async def time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['action'] = 'time'

    kb = [
        [
            types.KeyboardButton(text="📋Доп. информация"),
            types.KeyboardButton(text="✉Отправить")
        ],
        [
            types.KeyboardButton(text="↩Меню")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Во сколько сбор?", reply_markup=keyboard)


# Хэндлер на команду /Доп.информация
@dp.message_handler(text=["📋Доп. информация"])
async def staff_list(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['action'] = 'comment'

    kb = [
        [
            types.KeyboardButton(text="✉Отправить"),
            types.KeyboardButton(text="↩Меню")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer('Введите дополнительную информацию:', reply_markup=keyboard)


# Хэндлер на команду /Отправить
@dp.message_handler(text=["✉Отправить"])
async def staff_list(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        st = data['staff']
        ob = data['objects']

    # контроль ввода всех данных
    if 'date' not in data:
        async with state.proxy() as data:
            data['action'] = 'date'

        kb = [
            [
                types.KeyboardButton(text="✉Отправить"),
                types.KeyboardButton(text="↩Меню")
            ]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer('Забыли указать дату выезда. Введите дату:', reply_markup=keyboard)

    elif 'time' not in data:
        async with state.proxy() as data:
            data['action'] = 'time'

        kb = [
            [
                types.KeyboardButton(text="✉Отправить"),
                types.KeyboardButton(text="↩Меню")
            ]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer('Забыли указать время сбора. Введите время:', reply_markup=keyboard)

    else:
        date = data['date']
        tm = data['time']

        kb = [
            [
                types.KeyboardButton(text="✅Подтвердить"),
                types.KeyboardButton(text="↩Меню")
            ]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer('Все верно?', reply_markup=keyboard)

        # Действия при наличии/отсутствии доп. информации
        if 'comment' in data:
            com = data['comment']

            text_message = f"Дата: {date}\n\n" \
                           f"Бригада: {', '.join(st)}\n\n" \
                           f"Объект: {', '.join(ob)}\n\n" \
                           f"Сбор у склада: в {tm}\n\n" \
                           f"Доп. информация: {com}"

            async with state.proxy() as data:
                data['message'] = text_message

            await message.answer(text_message, reply_markup=keyboard)

        else:
            text_message = f"Дата: {date}\n\n" \
                           f"Бригада: {', '.join(st)}\n\n" \
                           f"Объект: {', '.join(ob)}\n\n" \
                           f"Сбор у склада: в {tm}"

            async with state.proxy() as data:
                data['message'] = text_message

            await message.answer(text_message, reply_markup=keyboard)


# Хэндлер на команду /Подтвердить (отправляет готовое сообщение в группу)
@dp.message_handler(text=["✅Подтвердить"])
async def staff_list(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text_message = data['message']

    await bot.send_message(chat_id=chat_id, text=text_message)

    kb = [
        [
            types.KeyboardButton(text="📁Списки"),
            types.KeyboardButton(text="🚐Выезды")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Сообщение отправлено", reply_markup=keyboard)

    await state.finish()


# Хэндлер inline-кнопок
@dp.callback_query_handler()
async def callbacks_num(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        key = data['key']
        try:
            data_list = data[key]
        except KeyError:
            data_list = list()

    if callback.data != 'finish':
        data_list.append(callback.data)
        async with state.proxy() as data:
            data[key] = data_list

    else:
        async with state.proxy() as data:
            data_list = data[key]

        await callback.message.edit_text(f"{', '.join(data_list)}")


# Хэндлер сообщений пользователя
@dp.message_handler()
async def user_data(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            action = data['action']

        # сохранение вводимых пользователем данных (при формировании сообщения о выезде)
        if action == 'comment' or action == 'date' or action == 'time':
            async with state.proxy() as data:
                data[action] = message.text

        elif action == 'Добавить':
            async with state.proxy() as data:
                key = data['key']

            add_data(message, key)

            await state.finish()

        elif action == 'Удалить':
            async with state.proxy() as data:
                key = data['key']

            error = delete_data(message, key)

            # контроль ввода
            if error == 'error':
                await message.answer('Некорректный ввод')

            await state.finish()

        if action == 'Добавить' or action == 'Удалить':
            kb = [
                [
                    types.KeyboardButton(text="Сотрудники🧑‍🌾"),
                    types.KeyboardButton(text="Объекты🏠")
                ],
                [
                    types.KeyboardButton(text="↩Меню")
                ]
            ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

            staff_list, objects_list = message_lists()

            await message.answer(f"Сотрудники 🧑‍🌾:\n{staff_list}\n\n"
                                 f"Объекты 🏠:\n{objects_list}\n\n", reply_markup=keyboard)

    except KeyError:
        await message.answer('Некорректный ввод')


if __name__ == "__main__":
    executor.start_polling(dp)

