from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db


class FSMAdmin1(StatesGroup):
    photo = State()
    name = State()
    size = State()
    price = State()


# Работа с загрузкой товаров. Подключение к БД. Потом привяжем к кнопкам, настроим доступы и тд :Р
# @dp.message_handler(commands='Загрузить1', state=None)
async def cm_start(message: types.Message):
    await FSMAdmin1.photo.set()
    await message.reply('Загрузите фото.')


# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
# async def cancel_handler(message: types.Message, state: FSMContext):
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#     await state.finish()
#     await message.reply('OK')


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
        data1['price'] = int(message.text)
    # async with state.proxy() as data:
    #     await message.reply(str(data))
    await sqlite_db.sql_add_command1(state)
    await state.finish()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands=['Загрузить1'], state=None)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin1.photo)
    dp.register_message_handler(load_name, state=FSMAdmin1.name)
    dp.register_message_handler(load_size, state=FSMAdmin1.size)
    dp.register_message_handler(load_price, state=FSMAdmin1.price)
