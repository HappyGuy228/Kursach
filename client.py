from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from keyboards import kb_client_settings
from data_base import sqlite_db


class FSM_review(StatesGroup):
    product_id = State()
    review = State()


# @dp.message_handler(commands='Написать отзыв', state=None)
async def cm_start(message: types.Message):
    await FSM_review.product_id.set()
    await message.reply('Введите ID товара, на который хотите написать отзыв.')


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
    

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cm_start, lambda message: message.text == 'Написать отзыв', state=None)
    dp.register_message_handler(load_product_id, state=FSM_review.product_id)
    dp.register_message_handler(load_review, state=FSM_review.review)


