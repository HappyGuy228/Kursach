import sqlite3 as sq
from create_bot import bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

ID = None


def sql_start():
    global base, cur
    base = sq.connect('stivaletto_shop_db.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS user(user_id INT PRIMARY KEY, name TEXT, phone TEXT, address TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS catalog(product_id TEXT PRIMARY KEY, category TEXT, photo TEXT, name TEXT, size TEXT, price INT)')
    base.execute('CREATE TABLE IF NOT EXISTS reviews(product_id TEXT PRIMARY KEY, review LONGTEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS categories(category_id INT PRIMARY KEY, category_name TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS cart(id INTEGER PRIMARY KEY, user_id INT, product_id TEXT, name TEXT, quantity INT, total_price INT)')
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


async def check_product_id(product_id):
    result = cur.execute(f"SELECT * FROM catalog WHERE product_id = '{product_id}'").fetchone()
    if result is not None:
        return True
    else:
        return False


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
    result_set = cur.execute(f'SELECT product_id, photo, name, size, price FROM catalog WHERE category = "{category}"').fetchall()
    for row in result_set:
        product_id, photo, name, size, price = row
        await bot.send_photo(callback_query.from_user.id, photo,
                             f'Идентификатор: {product_id}\nНазвание: {name}\nРазмер: {size}\nЦена: {price}')
        await bot.send_message(callback_query.from_user.id, text="***", reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('Добавить в корзину', callback_data='add')))


async def sql_read_reviews(message):
    for ret in cur.execute('SELECT * FROM reviews').fetchall():
        await bot.send_message(message.from_user.id, f'Идентификатор товара: {ret[0]}\nОтзыв: {ret[1]}')


async def get_product_price(product_id):
    result_set = cur.execute('SELECT price FROM catalog WHERE product_id = ?', (product_id,)).fetchone()
    if result_set:
        return result_set[0]
    else:
        return None


async def sql_add_command_cart(callback_query):
    # user_id = callback_query.from_user.id
    # product_id = callback_query.data.split()[1]
    #
    # cur.execute('SELECT * FROM cart WHERE user_id=?', (user_id,))
    # cart = cur.fetchone()
    # if not cart:
    #     cur.execute('INSERT INTO cart (user_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?)',
    #                 (user_id, '', '', 0))
    #     base.commit()
    #
    # cur.execute('SELECT * FROM cart WHERE user_id=?', (user_id,))
    # cart = cur.fetchone()
    # product_ids = cart[2].split(',')
    # product_counts = cart[3].split(',')
    # total_price = cart[4]
    #
    # if product_id in product_ids:
    #     index = product_ids.index(product_id)
    #     product_counts[index] = str(int(product_counts[index].replace(',', '.')) + 1)
    # else:
    #     product_ids.append(product_id)
    #     product_counts.append('1')
    #
    # product_ids_str = ', '.join(product_ids)
    # product_counts_str = ', '.join(product_counts)
    # total_price += await get_product_price(product_id)
    # cur.execute('UPDATE cart SET product_id=?, quantity=?, total_price=? WHERE user_id=?',
    #             (product_ids_str, product_counts_str, total_price, user_id))
    # base.commit()
    # await bot.answer_callback_query(callback_query.id, text='Товар добавлен в корзину')


# async def sql_read_cart(message):
    # cart_items = cur.execute('SELECT * FROM cart').fetchall()
    #
    # if not cart_items:
    #     await message.answer("Ваша корзина пуста.")
    #     return
    #
    # total_items = 0
    # total_price = 0
    #
    # cart_message = "Для очистки корзины используйте команду /empty\nВаша корзина:\n"
    # for item in cart_items:
    #     total_items += int(float(item[3].replace(',', '.')))
    #     total_price += item[4] * int(float(item[3].replace(',', '.')))
    #     cart_message += f"\n{item[1]} ({item[3]} шт.) - {item[4]} руб. за шт."
    #
    # cart_message += f"\n\nВсего товаров: {total_items}"
    # cart_message += f"\nОбщая стоимость: {total_price} руб."
    #
    # inline_keyboard = InlineKeyboardMarkup()
    # inline_keyboard.add(InlineKeyboardButton(text="Купить", callback_data="buy"))
    # await message.answer(cart_message, reply_markup=inline_keyboard)


async def empty_cart(message):
    user_id = message.from_user.id
    cur.execute('DELETE FROM cart WHERE user_id=?', (user_id,))
    base.commit()
    await message.answer("Корзина очищена")
