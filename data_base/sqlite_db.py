import sqlite3 as sq
from bot import dp


def sql_start():
    global base, cur
    base = sq.connect('stivaletto_shop_db.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS user(name TEXT PRIMARY KEY, phone TEXT, address TEXT)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO user VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()
