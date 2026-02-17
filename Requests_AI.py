# -*- coding: utf-8 -*-
import os
import aiohttp
import asyncio
from dotenv import load_dotenv



class AI:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OR_TOKEN")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openrouter/free"  # бесплатный роутер

    async def send_request(self, messages, max_tokens=300, temperature=1.0):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload, headers=headers) as resp:
                data = await resp.json()

        if "error" in data:
            # если OpenRouter вернул ошибку
            error = data["error"]
            raise Exception(f"OpenRouter API error: {error}")

        # возврат текста модели
        if data["choices"][0]["message"]["content"] != "":
            return data["choices"][0]["message"]["content"]
        return data["choices"][0]["message"]["reasoning"]

    async def requests(self, age, favoriteGenres, data: tuple, looking=""):
        mood, company, time = data

        messages = [
            {
                "role": "user",
                "content": f"""
                Я хочу посмотреть фильм, и не могу выбрать...
                Мой возраст: {age}
                Любимые жанры: {favoriteGenres}
                Настроение: {mood}
                Компания: {company}
                Время: {time}
                Не показывай фильмы из списка: {looking}
                Говори на русском языке
                не делай никаких вступлений, сразу начинай называть фильмы от лучшего к худшему (по твоему мнению)
                к каждому фильму дай небольшое описание, но без спойлеров
                дай мне 5 фильмов на выбор
                """
            }
        ]

        # асинхронный вызов OpenRouter
        result = await self.send_request(messages, max_tokens=1200, temperature=0.7)
        return result

    async def get_filmName(self, text):
        messages = [
            {
                "role": "user",
                "content": f"Достань из текста названия фильмов: {text}. Напиши через ';'"
            }
        ]
        return await self.send_request(messages, max_tokens=300)


# для теста
async def main():
    ai = AI()
    res = await ai.requests(
        19,
        "Триллер Ужасы Комедия Мистика",
        ("Хочу смеяться", "С друзьями", "100‑140мин")
    )
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
