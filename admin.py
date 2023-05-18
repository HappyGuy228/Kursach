from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db
from create_bot import bot, dp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

ID = None


class FSMAdmin_product(StatesGroup):
    product_id = State()
    category = State()
    photo = State()
    name = State()
    size = State()
    price = State()


async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Вы модератор. Теперь вы можете занести товары или новые категории, а также их удалить.'
                                                 'Введите команду /Загрузить_товар для загрузки товара или /Категория для добавления новой категории.'
                                                 'Введите команду /Удалить_товар для удаления товара или /Удалить_категорию для удаления категории.')
    await message.delete()


async def cm_start(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdmin_product.product_id.set()
        await message.reply('Введите ID товара.')


async def cancel_handler_admin_goods(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')


async def load_product_id(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['product_id'] = message.text
        await FSMAdmin_product.next()
        await message.reply("Введите категорию")


async def load_category(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        category_name = message.text
        if not await sqlite_db.check_category(category_name):
            await message.reply("Такая категория не найдена, повторите ввод.")
            return
        async with state.proxy() as data1:
            data1['category'] = message.text
        await FSMAdmin_product.next()
        await message.reply("Загрузите фото")


async def load_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['photo'] = message.photo[0].file_id
        await FSMAdmin_product.next()
        await message.reply("Теперь введите название")


async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['name'] = message.text
        await FSMAdmin_product.next()
        await message.reply("Введите размер")


async def load_size(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['size'] = message.text
        await FSMAdmin_product.next()
        await message.reply("Введите цену")


async def load_price(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['price'] = message.text
        await sqlite_db.sql_add_command_catalog(state)
        await state.finish()
        await message.reply("Товар добавлен")


class FSMAdmin_category(StatesGroup):
    category_id = State()
    category = State()


async def cm_start1(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdmin_category.category_id.set()
        await message.reply('Введите ID категории.')


async def set_id(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['category_id'] = message.text
        await FSMAdmin_category.next()
        await message.answer("Введите название категории")


async def set_category(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data1:
            data1['category_name'] = message.text
        await sqlite_db.sql_add_command_category(state)
        await state.finish()
        await message.reply("Категория добавлена!")


@dp.message_handler(commands='Удалить_товар')
async def delete_product(message: types.Message):
    if message.from_user.id == ID:
        read = await sqlite_db.sql_read_catalog1()
        for ret in read:
            product_id, photo, name, size, price = ret
            await bot.send_photo(message.from_user.id, photo,
                                 f'Идентификатор: {product_id}\nНазвание: {name}\nРазмер: {size}\nЦена: {price}')
            await bot.send_message(message.from_user.id, text="***", reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton('Удалить', callback_data=f'delete pr {product_id}')))


@dp.callback_query_handler(Text(startswith='delete pr '))
async def delete_product(callback: types.CallbackQuery):
    await sqlite_db.sql_delete_product(callback.data.replace('delete pr ', ''))
    await callback.answer('Товар удален!', show_alert=True)
    await callback.answer()


@dp.message_handler(commands='Удалить_категорию')
async def delete_product(message: types.Message):
    if message.from_user.id == ID:
        read = await sqlite_db.sql_read_categories()
        for ret in read:
            category_id, category_name = ret
            await bot.send_message(message.from_user.id, f'Идентификатор: {category_id}\nНазвание: {category_name}')
            await bot.send_message(message.from_user.id, text="***", reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton('Удалить', callback_data=f'delete cat {category_id}')))


@dp.callback_query_handler(Text(startswith='delete cat '))
async def delete_product(callback: types.CallbackQuery):
    await sqlite_db.sql_delete_category(callback.data.replace('delete cat ', ''))
    await callback.answer('Категория удалена!', show_alert=True)
    await callback.answer()


def register_handlers_admin1(dp: Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['moderator'], is_chat_admin=True)
    dp.register_message_handler(cm_start, commands=['Загрузить_товар'], state=None)
    dp.register_message_handler(cancel_handler_admin_goods, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler_admin_goods, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_product_id, state=FSMAdmin_product.product_id)
    dp.register_message_handler(load_category, state=FSMAdmin_product.category)
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin_product.photo)
    dp.register_message_handler(load_name, state=FSMAdmin_product.name)
    dp.register_message_handler(load_size, state=FSMAdmin_product.size)
    dp.register_message_handler(load_price, state=FSMAdmin_product.price)


def register_handlers_admin2(dp: Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['moderator'], is_chat_admin=True)
    dp.register_message_handler(cm_start1, commands=['Категория'], state=None)
    dp.register_message_handler(set_id, state=FSMAdmin_category.category_id)
    dp.register_message_handler(set_category, state=FSMAdmin_category.category)

