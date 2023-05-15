import sqlite3 as sq
from create_bot import bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types

ID = None


def sql_start():
    global base, cur
    base = sq.connect('stivaletto_shop_db.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS user(user_id INT PRIMARY KEY, user_name TEXT, phone TEXT, address TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS catalog(product_id INT PRIMARY KEY, category TEXT, photo TEXT, product_name TEXT, size TEXT, price INT)')
    base.execute('CREATE TABLE IF NOT EXISTS reviews(product_id INT PRIMARY KEY, review LONGTEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS categories(category_id INT PRIMARY KEY, category_name TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS cart(id INTEGER PRIMARY KEY, user_id INT, product_id INT, product_name TEXT)')
    base.commit()


async def sql_add_command_user(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO user VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_add_command_catalog(state):
    async with state.proxy() as data1:
        cur.execute('INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)', tuple(data1.values()))
        base.commit()


async def sql_add_command_review(state):
    async with state.proxy() as data2:
        cur.execute('INSERT INTO reviews VALUES (?, ?)', tuple(data2.values()))
        base.commit()


async def sql_add_command_category(state):
    async with state.proxy() as data2:
        cur.execute('INSERT INTO categories VALUES (?, ?)', tuple(data2.values()))
        base.commit()


async def check_category(category_name):
    result = cur.execute(f"SELECT * FROM categories WHERE category_name = '{category_name}'").fetchone()
    if result is not None:
        return True
    else:
        return False


async def check_user_exist(id):
    result = cur.execute(f"SELECT * FROM user WHERE user_id = '{id}'").fetchone()
    if result is not None:
        return True
    else:
        return False


async def check_product_id(product_id):
    result = cur.execute(f"SELECT * FROM catalog WHERE product_id = '{product_id}'").fetchone()
    if result is not None:
        return True
    else:
        return False


async def get_product_name(product_id):
    cur.execute('SELECT product_name FROM catalog WHERE product_id = ?', (product_id,))
    result = cur.fetchone()

    if result is not None:
        return result[0]
    else:
        return "Название не найдено"


async def sql_read_user(message):
    # result_set = cur.execute(f"SELECT * FROM user WHERE user_id = '{ID}'").fetchone()
    # for row in result_set:
    #     user_id, name, phone, address = row
    #     await bot.send_message(ID, text=f'ID: {user_id}\nИмя: {name}\nНомер: {phone}\nАдрес: {address}')
    for ret in cur.execute(f"SELECT * FROM user WHERE user_id = '{message.from_user.id}'").fetchall():
        await bot.send_message(message.from_user.id, f'Имя: {ret[1]}\nТелефон: {ret[2]}\nАдрес: {ret[3]}')


async def sql_delete_user(message):
    cur.execute(f'DELETE FROM user WHERE user_id={message.from_user.id}')
    base.commit()


async def sql_read_catalog(callback_query, category):
    result_set = cur.execute(f'SELECT product_id, photo, product_name, size, price FROM catalog WHERE category = "{category}"').fetchall()
    for row in result_set:
        product_id, photo, name, size, price = row
        await bot.send_photo(callback_query.from_user.id, photo,
                             f'Идентификатор: {product_id}\nНазвание: {name}\nРазмер: {size}\nЦена: {price}')
        await bot.send_message(callback_query.from_user.id, text="***", reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('Добавить в корзину', callback_data=f'add: {product_id}')))


async def sql_read_reviews(message):
    for ret in cur.execute('SELECT * FROM reviews').fetchall():
        await bot.send_message(message.from_user.id, f'Идентификатор товара: {ret[0]}\nОтзыв: {ret[1]}')


async def get_product_price(product_id):
    cur.execute('SELECT price FROM catalog WHERE product_id = ?', (product_id,))
    result = cur.fetchone()
    if result is not None:
        return result[0]
    else:
        return "Такой цены нет"


async def add_to_cart(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    product_id = int(callback_query.data.split(':')[1])
    product_name = await get_product_name(product_id)  # Здесь вы должны реализовать логику получения названия товара из каталога

    # Добавляем товар в корзину
    cur.execute('''
            INSERT INTO cart (user_id, product_id, product_name)
            VALUES (?, ?, ?)
        ''', (user_id, product_id, product_name))
    base.commit()

    await bot.send_message(user_id, f'Товар "{product_name}" добавлен в корзину!')


async def sql_read_cart(message):
    cart_items = cur.execute('SELECT * FROM cart').fetchall()

    if not cart_items:
        await message.answer("Ваша корзина пуста.")
        return

    total_items = 0
    total_price = 0

    cart_message = "Для опустошения корзины используйте команду /empty\nВаша корзина:\n"
    for item in cart_items:
        while total_items < item[0]:
            total_items += 1
        # total_items += float(item[3].replace(',', '.'))
        # total_price += item[4] * float(item[3].replace(',', '.'))
        # cart_message += f"\n{item[2]} ({item[3]} шт.) - {item[4]} руб. за шт."
        price = await get_product_price(product_id=item[2])
        total_price += price
        cart_message += f'\n{item[3]} - {price} руб.'

    cart_message += f"\n\nВсего товаров: {total_items}"
    cart_message += f"\nОбщая стоимость: {total_price} руб."

    inline_buy = InlineKeyboardMarkup()
    inline_buy.add(InlineKeyboardButton(text="Купить", callback_data="buy"))
    await message.answer(cart_message, reply_markup=inline_buy)


async def empty_cart(message):
    user_id = message.from_user.id
    cur.execute('DELETE FROM cart WHERE user_id=?', (user_id,))
    base.commit()
    await message.answer("Корзина очищена")
