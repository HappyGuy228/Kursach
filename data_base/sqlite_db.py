import sqlite3 as sq
from bot import dp
from bot import bot


def sql_start():
    global base, cur
    base = sq.connect('stivaletto_shop_db.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS user(name TEXT PRIMARY KEY, phone TEXT, address TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS katalog(photo TEXT, name TEXT PRIMARY KEY, size TEXT, price TEXT)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO user VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_add_command1(state):
    async with state.proxy() as data1:
        cur.execute('INSERT INTO katalog VALUES (?, ?, ?, ?)', tuple(data1.values()))
        base.commit()


async def sql_read(message):
    for ret in cur.execute('SELECT * FROM katalog').fetchall():
        await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}]\nРазмер: {ret[2]}\nЦена: {ret[3]}')
