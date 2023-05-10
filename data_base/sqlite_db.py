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
    base.execute('CREATE TABLE IF NOT EXISTS katalog(product_id TEXT PRIMARY KEY, photo TEXT, name TEXT, size TEXT, price TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS reviews(product_id TEXT PRIMARY KEY, review LONGTEXT)')
    base.commit()


async def sql_add_command_user(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO user VALUES (?, ?, ?, ?)', tuple(data.values()))
        base.commit()

async def sql_add_command_katalog(state):
    async with state.proxy() as data1:
        cur.execute('INSERT INTO katalog VALUES (?, ?, ?, ?, ?)', tuple(data1.values()))
        base.commit()


async def sql_add_command_review(state):
    async with state.proxy() as data2:
        cur.execute('INSERT INTO reviews VALUES (?, ?)', tuple(data2.values()))
        base.commit()


async def check_product_id(product_id):
    result = cur.execute(f"SELECT * FROM katalog WHERE product_id = '{product_id}'").fetchone()
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

async def sql_read_katalog(message):
    result_set = cur.execute('SELECT * FROM katalog').fetchall()
    for row in result_set:
        product_id, photo, name, size, price = row
        await bot.send_photo(message.from_user.id, photo, f'Идентификатор: {product_id}\nНазвание: {name}\nРазмер: {size}\nЦена: {price}')
        await bot.send_message(message.from_user.id, text="***", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Добавить в корзину', callback_data=f'add {product_id}')))


async def sql_read_reviews(message):
    for ret in cur.execute('SELECT * FROM reviews').fetchall():
        await bot.send_message(message.from_user.id, f'Идентификатор товара: {ret[0]}\nОтзыв: {ret[1]}')


