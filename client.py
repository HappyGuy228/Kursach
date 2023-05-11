from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db

ID = None


class FSM_review(StatesGroup):
    product_id = State()
    review = State()


# @dp.message_handler(commands='Написать отзыв', state=None)
async def cm_start_review(message: types.Message):
    await FSM_review.product_id.set()
    await message.reply('Введите ID товара, на который хотите написать отзыв.')


async def cancel_handler_client_review(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')


# @dp.message_handler(state=FSM_review.product_id)
async def load_product_id(message: types.Message, state: FSMContext):
    product_id = message.text
    if not await sqlite_db.check_product_id(product_id):
        await message.reply("Товар с таким ID не найден, пожалуйста, повторите ввод.")
        return
    async with state.proxy() as data2:
        data2['product_id'] = message.text
    await FSM_review.next()
    await message.reply("Напишите отзыв")


# @dp.message_handler(state=FSM_review.review)
async def load_review(message: types.Message, state: FSMContext):
    async with state.proxy() as data2:
        data2['review'] = message.text
    await sqlite_db.sql_add_command_review(state)
    await state.finish()


##################################
class FSM_user(StatesGroup):
    user_id = State()
    name = State()
    phone = State()
    address = State()


async def cm_start_user(message: types.Message):
    global ID
    ID = message.from_user.id
    if await sqlite_db.check_user_exist(ID):
        await message.reply("Пользователь с вашим ID уже существует.")
        return
    await FSM_user.user_id.set()


# Выход из состояний
# @dp.message_handler(state="*", commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler_client_user(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')


# @dp.message_handler(state=FSMAdmin.name)
async def load_user_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = ID
    await FSM_user.next()
    await message.reply("Введите ваше ФИО")


# @dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSM_user.next()
    await message.reply("Введите ваш номер")


# @dp.message_handler(state=FSMAdmin.phone)
async def load_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = int(message.text)
    await FSM_user.next()
    await message.reply("Укажите ваш адрес")


# @dp.message_handler(state=FSMAdmin.address)
async def load_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
    await sqlite_db.sql_add_command_user(state)
    await state.finish()


def register_handlers_client_review(dp: Dispatcher):
    dp.register_message_handler(cm_start_review, lambda message: message.text == 'Написать отзыв', state=None)
    dp.register_message_handler(cancel_handler_client_review, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler_client_review, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_product_id, state=FSM_review.product_id)
    dp.register_message_handler(load_review, state=FSM_review.review)


def register_handlers_client_user(dp: Dispatcher):
    dp.register_message_handler(cm_start_user, lambda message: message.text == 'Регистрация', state=None)
    dp.register_message_handler(cancel_handler_client_user, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler_client_user, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_user_id, state=FSM_user.user_id)
    dp.register_message_handler(load_name, state=FSM_user.name)
    dp.register_message_handler(load_number, state=FSM_user.phone)
    dp.register_message_handler(load_address, state=FSM_user.address)
