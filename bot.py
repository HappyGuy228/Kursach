from aiogram import types, executor
from keyboards import kb_client_settings, kb_client_menu, kb_client_review
from aiogram.types import ReplyKeyboardRemove
from inline import keyboard
from data_base import sqlite_db
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
import admin
import client

client.register_handlers_client_user(dp)
client.register_handlers_client_review(dp)
admin.register_handlers_admin1(dp)
admin.register_handlers_admin2(dp)


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


@dp.message_handler(commands='empty')
async def cart_empty(message: types.Message):
    await sqlite_db.empty_cart1(message)


@dp.message_handler(lambda message: message.text in ['📦Каталог', 'ℹ️Помощь', '🛒Корзина', '📝История заказов', '⚙️Настройки', '💬Отзывы'])
async def keyboard_handler_menu(message: types.Message):
    match message.text:
        case "📦Каталог":
            await message.delete()
            await message.answer("Здесь находится каталог", reply_markup=keyboard)
        case "ℹ️Помощь":
            await message.delete()
            await message.answer(text=result, reply_markup=ReplyKeyboardRemove())
        case "🛒Корзина":
            await message.delete()
            await message.answer("Здесь будет корзина")
            await sqlite_db.sql_read_cart(message)
        case "📝История заказов":
            await message.delete()
            await message.answer("Здесь будут заказы")
            await sqlite_db.sql_read_orders(message)
        case "⚙️Настройки":
            await message.delete()
            await message.answer("Здесь будут настройки", reply_markup=kb_client_settings)
        case "💬Отзывы":
            await message.delete()
            await message.answer("Здесь будут отзывы", reply_markup=kb_client_review)


@dp.message_handler(lambda message: message.text in ['Посмотреть отзывы', 'Написать отзыв', 'Назад'])
async def keyboard_handler_review(message: types.Message):
    match message.text:
        case 'Посмотреть отзывы':
            await sqlite_db.sql_read_reviews(message)
        case 'Написать отзыв':
            await message.answer('Здесь можно написать отзыв')
        case "Назад":
            await message.delete()
            await message.answer('Вы вернулись в главное меню', reply_markup=kb_client_menu)


@dp.message_handler(lambda message: message.text in ['Регистрация', 'Данные', 'Удалить', 'Назад'])
async def keyboard_handler_settings(message: types.Message):
    match message.text:
        case "Регистрация":
            await message.delete()
        case "Данные":
            await message.delete()
            await sqlite_db.sql_read_user(message)
        case "Удалить":
            await message.delete()
            await sqlite_db.sql_delete_user(message)
            await message.answer("Ваши данные удалены")
        case "Назад":
            await message.delete()
            await message.answer('Вы вернулись в главное меню', reply_markup=kb_client_menu)


@dp.callback_query_handler(lambda x: x.data and x.data in ['Сапоги', 'Ботинки', 'Туфли'])
async def process_category(callback_query: types.CallbackQuery):
    category = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    await sqlite_db.sql_read_catalog(callback_query, category)


@dp.callback_query_handler(Text(startswith='add: '))
async def add_cart(callback: types.CallbackQuery):
    await sqlite_db.add_to_cart(callback)
    await callback.answer()


@dp.callback_query_handler(Text('buy'))
async def add_order(callback: types.CallbackQuery):
    await sqlite_db.add_to_orders(callback)
    await sqlite_db.empty_cart2(callback)
    await callback.answer()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
