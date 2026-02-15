import aiosqlite
import asyncio
from datetime import date, datetime


class DataBaseUsers:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path

    async def connect(self):
        conn = await aiosqlite.connect(self.db_path, timeout=30)
        conn.row_factory = aiosqlite.Row
        return conn

    async def create_db(self):
        conn = await self.connect()
        try:
            async with conn.cursor() as cursor:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER NOT NULL,
                    login TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    favoriteGenres TEXT NOT NULL
                )
                """
                await cursor.execute(create_table_query)
                await conn.commit()
        finally:
            await conn.close()

    async def verify_user(self, tg_id):
        conn = await self.connect()
        try:
            async with conn.cursor() as cursor:
                veryfi_cuery = "SELECT * FROM users WHERE tg_id = ?"
                await cursor.execute(veryfi_cuery, (tg_id,))
                rows = await cursor.fetchall()
                user = [dict(row) for row in rows]
                if user == []:
                    return False
                return True
        finally:
            await conn.close()

    async def add_data(self, tg_id, login, age, favoriteGenres):
        conn = await self.connect()
        date_create = str(datetime.now().date()).replace("-", ".")
        try:
            async with conn.cursor() as cursor:
                insert_query = """
                INSERT INTO users (tg_id, login, age, favoriteGenres)
                VALUES (?, ?, ?, ?)
                """
                await cursor.execute(insert_query,
                                     (tg_id, login, age, favoriteGenres))
                await conn.commit()
        finally:
            await conn.close()

    async def get_data(self):
        conn = await self.connect()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM users")
                rows = await cursor.fetchall()
                users = [dict(row) for row in rows]
                return users
        finally:
            await conn.close()

    async def get_data_id(self, user_id):
        conn = await self.connect()
        try:
            get_data_id_query = "SELECT * FROM users WHERE tg_id = ?"
            async with conn.cursor() as cursor:
                await cursor.execute(get_data_id_query, (user_id,))
                rows = await cursor.fetchall()
                user = [dict(row) for row in rows]
                return user
        finally:
            await conn.close()

    async def update_favoriteGenres(self, user_id, favoriteGenres):
        conn = await self.connect()
        try:
            update_query = "UPDATE users SET favoriteGenres = ? WHERE tg_id = ?"
            async with conn.cursor() as cursor:
                await cursor.execute(update_query, (favoriteGenres, user_id))
                await conn.commit()
        finally:
            await conn.close()




async def main():
    db = DataBaseUsers("database.db")
    await db.create_db()
    await db.add_data(12345, "login", "21", "")
    print(await db.verify_user(4563))



if __name__ == "__main__":
    asyncio.run(main())