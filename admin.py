from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db


class FSMAdmin1(StatesGroup):
    product_id = State()
    photo = State()
    name = State()
    size = State()
    price = State()


# Работа с загрузкой товаров. Подключение к БД. Потом привяжем к кнопкам, настроим доступы и тд :Р
# @dp.message_handler(commands='Загрузить1', state=None)
async def cm_start(message: types.Message):
    await FSMAdmin1.product_id.set()
    await message.reply('Введите ID товара.')


# @dp.message_handler(state=FSMAdmin1.product_id)
async def load_product_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data1:
        data1['product_id'] = message.text
    await FSMAdmin1.next()
    await message.reply("Загрузите фото")


# @dp.message_handler(content_types=['photo'], state=FSMAdmin1.photo)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data1:
        data1['photo'] = message.photo[0].file_id
    await FSMAdmin1.next()
    await message.reply("Теперь введи название")


# @dp.message_handler(state=FSMAdmin1.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data1:
        data1['name'] = message.text
    await FSMAdmin1.next()
    await message.reply("Введите размер")


# @dp.message_handler(state=FSMAdmin1.size)
async def load_size(message: types.Message, state: FSMContext):
    async with state.proxy() as data1:
        data1['size'] = message.text
    await FSMAdmin1.next()
    await message.reply("Введите цену")


# @dp.message_handler(state=FSMAdmin1.price)
async def load_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data1:
        data1['price'] = message.text
    await sqlite_db.sql_add_command_katalog(state)
    await state.finish()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands=['Загрузить1'], state=None)
    dp.register_message_handler(load_product_id, state=FSMAdmin1.product_id)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin1.photo)
    dp.register_message_handler(load_name, state=FSMAdmin1.name)
    dp.register_message_handler(load_size, state=FSMAdmin1.size)
    dp.register_message_handler(load_price, state=FSMAdmin1.price)
