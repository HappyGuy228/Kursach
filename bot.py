from aiogram import Bot, types, Dispatcher, executor
from config import TOKEN
from keyboards import kb_client_settings, kb_client_menu, kb_client_review
from aiogram.types import ReplyKeyboardRemove
from inline import keyboard
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db
import admin
# import client

storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
# client.register_handlers_client(dp)
admin.register_handlers_client(dp)

async def on_startup(_):
    print("Я запустился!")
    sqlite_db.sql_start()

HELP_MESSAGE = """Данный бот является магазином по продаже обуви
В разделе 'Каталог' Вы можете найти список всех товаров, отсортированных по категориям
В разделе 'Корзина' Вы можете найти список товаров, добавленных Вами для дальнейшей возможной покупки
В разделе 'Настройки' Вы можете поменять имя, телефон, адрес и город, использующихся для доставки
В разделе 'Заказы' Вы можете найти историю Ваших заказов
В разделе 'Отзывы' Вы можете посмотреть отзывы других людей или написать свой
Если у вас возникли вопросы или проблемы, свяжитесь с нами по электронной почте xxx@example.com"""

my_list = HELP_MESSAGE.split('\n')

result = ""
for item in my_list:
    result += f"\u2022 {item}\n"


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет! Добро пожаловать в телеграм-бота 'StivalettoShop'!", reply_markup=kb_client_menu)


@dp.message_handler(commands=['help'])
async def process_start_command(message: types.Message):
    await message.delete()
    await message.answer(text=result)


@dp.message_handler(lambda message: message.text in ['📦Каталог', 'ℹ️Помощь', '🛒Корзина', '📝Заказы', '⚙️Настройки', '💬Отзывы'])
async def keyboard_handler_menu(message: types.Message):
    match message.text:
        case "📦Каталог":
            await message.delete()
            await message.answer("Здесь будет каталог", reply_markup=keyboard)
            await sqlite_db.sql_read(message)
        case "ℹ️Помощь":
            await message.delete()
            await message.answer(text=result, reply_markup=ReplyKeyboardRemove())
        case "🛒Корзина":
            await message.delete()
            await message.answer("Здесь будет корзина")
        case "📝Заказы":
            await message.delete()
            await message.answer("Здесь будут заказы")
        case "⚙️Настройки":
            await message.delete()
            await message.answer("Здесь будут настройки", reply_markup=kb_client_settings)
        case "💬Отзывы":
            await message.delete()
            await message.answer("Здесь будут отзывы", reply_markup=kb_client_review)


@dp.message_handler(lambda message: message.text in['Посмотреть отзывы', 'Написать отзыв'])
async def keyboard_handler_review(message: types.Message):
    match message.text:
        case 'Посмотреть отзывы':
            await message.answer('Здесь будут отзывы')
        case 'Написать отзыв':
            await message.answer('Здесь можно написать отзыв')

@dp.message_handler(lambda message: message.text in ['Имя', 'Телефон', 'Адрес', 'Назад'])
async def keyboard_handler_settings(message: types.Message):
    match message.text:
        case "Имя":
            await message.delete()
            await message.answer("Здесь будет Имя")
            username = message.from_user.first_name
            await message.answer(f"Ваше имя: {username}\n"
                                 "Хотите поменять? Тогда запишите новое: ")
            # @dp.message_handler()
            # async def help(message: types.Message):
            #     username = message.text
            #     await message.answer(f'Новое имя: {username}', reply_markup=kb_client_settings)
        case "Телефон":
            await message.delete()
            await message.answer("Здесь будет телефон")
        case "Адрес":
            await message.delete()
            await message.answer("Здесь будет Адрес")
        case "Назад":
            await message.delete()
            await message.answer('Вы вернулись в главное меню', reply_markup=kb_client_menu)


@dp.callback_query_handler(lambda callback_query: callback_query.data in ['Категория 1', 'Категория 2', 'Категория 3'])
async def process_category(callback_query: types.CallbackQuery):
    category = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.reply(f'Это {category}!')

class FSMAdmin(StatesGroup):
    name = State()
    phone = State()
    address = State()

# Работа с загрузкой товаров. Подключение к БД. Потом привяжем к кнопкам, настроим доступы и тд :Р
@dp.message_handler(commands='Загрузить', state=None)
async def cm_start(message: types.Message):
    await FSMAdmin.name.set()
    await message.reply('Введите ваше ФИО.')

@dp.message_handler(state="*", commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')

@dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await message.reply("Введите ваш номер")


@dp.message_handler(state=FSMAdmin.phone)
async def load_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = int(message.text)
    await FSMAdmin.next()
    await message.reply("Укажите ваш адрес")


@dp.message_handler(state=FSMAdmin.address)
async def load_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
    # async with state.proxy() as data:
    #     await message.reply(str(data))
    await sqlite_db.sql_add_command(state)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
