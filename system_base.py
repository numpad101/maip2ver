import aiosqlite

DB_PATH = 'database.db'

async def create_tables():
    async with aiosqlite.connect(DB_PATH) as db:

        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                last_msg_time TEXT
            )
        ''')

        # Таблица админов
        await db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS price_ton (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                price REAL
            )
        ''')

        # Таблица products_tg_trade
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products_tg_trade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                price_default REAL,
                price_500plus REAL
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS products_tg_prem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                price REAL
            )
        ''')


        # Таблица products_supercell_brawl
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products_supercell_brawl (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                price REAL
            )
        ''')

        # Таблица products_supercell_clash
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products_supercell_clash (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                price REAL
            )
        ''')

        # Таблица products_supercell_clans
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products_supercell_clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                price REAL
            )
        ''')

        await db.execute(f'''
                    INSERT OR IGNORE INTO products_tg_trade (price_default, price_500plus)
                    VALUES (0, 0)
                ''')
        await db.execute(f'''
                    INSERT OR IGNORE INTO price_ton (price)
                    VALUES (0)
                ''')
        await db.commit()


async def add_product(table: str, label: str, price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f'''
            INSERT OR IGNORE INTO {table} (label, price)
            VALUES (?, ?)
        ''', (label, price))
        await db.commit()

async def update_product(table: str, product_id: int, label: str, price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f'''
            UPDATE {table} 
            SET label = ?, price = ? 
            WHERE id = ?
        ''', (label, price, product_id))
        await db.commit()

async def update_price_trade(price_default, price_500plus):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f'''
            UPDATE products_tg_trade 
            SET price_default = ?, price_500plus = ?
            WHERE id = 1
        ''', (price_default, price_500plus))
        await db.commit()

async def update_price_ton(price: float):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM price_ton WHERE id = 1') as cursor:
            row = await cursor.fetchone()
            if row is None:
                await db.execute('INSERT INTO price_ton (id, price) VALUES (?, ?)', (1, price))
            else:
                await db.execute('UPDATE price_ton SET price = ? WHERE id = 1', (price,))
        await db.commit()

async def delete_product(table_name: str, product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f'''
            DELETE FROM {table_name}
            WHERE id = ?
        ''', (product_id, ))
        await db.commit()


async def get_value(table: str, filters: dict = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        if filters:
            where_clause = " AND ".join([f"{k} = ?" for k in filters.keys()])
            sql = f"SELECT * FROM {table} WHERE {where_clause}"
            params = tuple(filters.values())
        else:
            sql = f"SELECT * FROM {table}"
            params = ()

        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()
        await cursor.close()

        return [dict(row) for row in rows]

async def add_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (id, username)
            VALUES (?, ?)
        ''', (user_id, username))
        await db.commit()

async def update_last_msg_time(user_id: int, last_msg_time: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            '''
            UPDATE users
            SET last_msg_time = ?
            WHERE id = ?
            ''',
            (last_msg_time, user_id)
        )
        await db.commit()

async def get_last_msg_time(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            '''
            SELECT last_msg_time FROM users WHERE id = ?
            ''',
            (user_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        if row:
            return row[0]  # last_msg_time как строка
        else:
            return None


async def add_admin(id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR IGNORE INTO admins (id)
            VALUES (?)
        ''', (id, ))
        await db.commit()


async def delete_admin(id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            DELETE FROM admins WHERE id = ?
        ''', (id,))
        await db.commit()


async def get_admins(table: str = 'admins', filters: dict = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        if filters:
            where_clause = " AND ".join([f"{k} = ?" for k in filters.keys()])
            sql = f"SELECT * FROM {table} WHERE {where_clause}"
            params = tuple(filters.values())
        else:
            sql = f"SELECT * FROM {table}"
            params = ()

        cursor = await db.execute(sql, params)
        rows = await cursor.fetchall()
        await cursor.close()

        return [dict(row).get('id') for row in rows]
