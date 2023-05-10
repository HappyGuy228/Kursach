from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db
from create_bot import bot, dp

ID = None

class FSMAdmin1(StatesGroup):
    product_id = State()
    photo = State()
    name = State()
    size = State()
    price = State()

#Получаем ID текущего модератора
# @dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Вы модератор. Теперь вы можете занести товары. Введите команду /Загрузить_товар.')
    await message.delete()

# Работа с загрузкой товаров. Подключение к БД. Потом привяжем к кнопкам, настроим доступы и тд :Р
# @dp.message_handler(commands='Загрузить1', state=None)
async def cm_start(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdmin1.product_id.set()
        await message.reply('Введите ID товара.')

# Выход из состояний
# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler_admin_goods(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')

# @dp.message_handler(state=FSMAdmin1.product_id)
async def load_product_id(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['product_id'] = message.text
        await FSMAdmin1.next()
        await message.reply("Загрузите фото")


# @dp.message_handler(content_types=['photo'], state=FSMAdmin1.photo)
async def load_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['photo'] = message.photo[0].file_id
        await FSMAdmin1.next()
        await message.reply("Теперь введи название")


# @dp.message_handler(state=FSMAdmin1.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['name'] = message.text
        await FSMAdmin1.next()
        await message.reply("Введите размер")


# @dp.message_handler(state=FSMAdmin1.size)
async def load_size(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['size'] = message.text
        await FSMAdmin1.next()
        await message.reply("Введите цену")


# @dp.message_handler(state=FSMAdmin1.price)
async def load_price(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['price'] = message.text
        await sqlite_db.sql_add_command_katalog(state)
        await state.finish()

def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['moderator'], is_chat_admin=True)
    dp.register_message_handler(cm_start, commands=['Загрузить_товар'], state=None)
    dp.register_message_handler(cancel_handler_admin_goods, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler_admin_goods, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_product_id, state=FSMAdmin1.product_id)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin1.photo)
    dp.register_message_handler(load_name, state=FSMAdmin1.name)
    dp.register_message_handler(load_size, state=FSMAdmin1.size)
    dp.register_message_handler(load_price, state=FSMAdmin1.price)


