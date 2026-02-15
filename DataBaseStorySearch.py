import aiosqlite
import asyncio
from datetime import date, datetime


class DataBaseStorySearch:
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
                CREATE TABLE IF NOT EXISTS storySearch (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER NOT NULL,
                    mood TEXT NOT NULL,
                    company TEXT NOT NULL,
                    time TEXT NOT NULL,
                    lookingFilm TEXT NOT NULL
                )
                """
                await cursor.execute(create_table_query)
                await conn.commit()
        finally:
            await conn.close()

    async def add_data(self, tg_id, mood, company, time, lookingFilm):
        conn = await self.connect()
        date_create = str(datetime.now().date()).replace("-", ".")
        try:
            async with conn.cursor() as cursor:
                insert_query = """
                INSERT INTO storySearch (tg_id, mood, company, time, lookingFilm)
                VALUES (?, ?, ?, ?, ?)
                """
                await cursor.execute(insert_query,
                                     (tg_id, mood, company, time, lookingFilm))
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
            get_data_id_query = "SELECT * FROM storySearch WHERE tg_id = ?"
            async with conn.cursor() as cursor:
                await cursor.execute(get_data_id_query, (user_id,))
                rows = await cursor.fetchall()
                user = [dict(row) for row in rows]
                return user
        finally:
            await conn.close()

    async def update_storyData(self, user_id, mood, company, time, lookingFilm):
        conn = await self.connect()
        try:
            updateMood_query = "UPDATE storySearch SET mood = ? WHERE tg_id = ?"
            updateCompany_query = "UPDATE storySearch SET company = ? WHERE tg_id = ?"
            updateTime_query = "UPDATE storySearch SET time = ? WHERE tg_id = ?"
            lookingFilm_query = "UPDATE storySearch SET lookingFilm = ? WHERE tg_id = ?"
            async with conn.cursor() as cursor:
                await cursor.execute(updateMood_query, (mood, user_id))
                await cursor.execute(updateCompany_query, (company, user_id))
                await cursor.execute(updateTime_query, (time, user_id))
                await cursor.execute(lookingFilm_query, (lookingFilm, user_id))
                await conn.commit()
        finally:
            await conn.close()




async def main():
    db = DataBaseStorySearch("database.db")
    await db.create_db()
    await db.add_data(12345, "login", "21", "", "")
    print(await db.get_data_id(543321))



if __name__ == "__main__":
    asyncio.run(main())