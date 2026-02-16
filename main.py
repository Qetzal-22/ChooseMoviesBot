from datetime import datetime

from aiogram import F, Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv
import os

import asyncio
import DataBaseUsers
import DataBaseStorySearch
import Requests_AI

load_dotenv()

TOKEN_BOT = os.getenv("TOKEN_API")

bot = Bot(TOKEN_BOT)
dp = Dispatcher(storage=MemoryStorage())
GENRES = [
    "Боевик", "Комедия", "Драма", "Ужаcсы",
    "Фантастика", "Мелодрама", "Триллер", "Детектив"
]

db_users = DataBaseUsers.DataBaseUsers("database.db")
db_storySearch = DataBaseStorySearch.DataBaseStorySearch("database.db")
ai = Requests_AI.AI()

class Register(StatesGroup):
    login = State()
    age = State()
    favoriteGenres = State()

class Test(StatesGroup):
    mood = State()
    company = State()
    time = State()

async def create_markup_Genres(user_id, doneType):
    user_id = str(user_id)
    builder = InlineKeyboardBuilder()
    data = await db_users.get_data_id(user_id)
    selected = data[0]["favoriteGenres"]

    for genre in GENRES:
        content = f"{'✅' if genre in selected else ''} {genre}"
        builder.button(text=content, callback_data=f"register_genres:{genre}:{doneType}")
    builder.button(text="✅Подтвердить", callback_data=f"{doneType}_doneGenres")
    builder.adjust(2)
    return builder.as_markup()

# command start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    btns = [
        [InlineKeyboardButton(text="Регистрация", callback_data="register_user")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    await message.answer("Зарегистрируйся чтоб начать подбор фильмов!", reply_markup=kb)

# developing command
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("All commands:\n1) /start - Start Bot\n2) /help - View Command Bot\n")

@dp.callback_query(F.data.startswith("register_user"))
async def cmd_register(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    print(f"пользователь с id {user_id} пытается зарегистироваться")
    if await db_users.verify_user(user_id):
        await callback.answer()
        await bot.send_message(
            chat_id=chat_id,
            text="Вы уже зарегистрированны"
        )
        return

    await callback.answer()

    await bot.send_message(
        chat_id=chat_id,
        text="Логин: "
    )
    await state.set_state(Register.login)

@dp.message(Register.login)
async def get_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    chat_id = message.chat.id

    await bot.send_message(
        chat_id=chat_id,
        text="Возраст: "
    )

    await state.set_state(Register.age)

@dp.message(Register.age)
async def get_age(message: types.Message, state: FSMContext):
    age = message.text
    if age.isdigit():
        if 0 > int(age) or 120 < int(age):
            await message.answer("Вы ввелии неправильный возраст. Возраст должен быть числом от 0 до 120.")
            await message.answer("Возраст: ")
            await state.set_state(Register.age)
            return
    else:
        await message.answer("Вы ввелии неправильный возраст. Возраст должен быть числом от 0 до 120.")
        await message.answer("Возраст: ")
        await state.set_state(Register.age)
        return

    await state.update_data(age=message.text)
    chat_id = message.chat.id
    user_id = message.from_user.id
    data = await state.get_data()
    login = data["login"]
    age = data["age"]

    await db_users.add_data(user_id, login, age, "")
    await db_storySearch.add_data(user_id, "", "", "", "")

    kb = await create_markup_Genres(user_id, "register")

    await bot.send_message(
        chat_id=chat_id,
        text="Выберете ваши любимые жанры: ",
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith("register_genres"))
async def select_genres(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    genre = callback.data.split(":")[1]
    doneType = callback.data.split(":")[2]
    user_id = str(callback.from_user.id)

    data = await db_users.get_data_id(user_id)
    genres = data[0]["favoriteGenres"]
    if not genre in genres:
        data = await db_users.get_data_id(user_id)
        genres = data[0]["favoriteGenres"]

        genres += f" {genre}"
        while "  " in genres:
            genres = genres.replace("  ", " ")

        await db_users.update_favoriteGenres(user_id, genres)
    else:
        data = await db_users.get_data_id(user_id)
        genres = data[0]["favoriteGenres"]

        genres = genres.replace(f"{genre}", "")
        while "  " in genres:
            genres = genres.replace("  ", " ")

        await db_users.update_favoriteGenres(user_id, genres)

    kb = await create_markup_Genres(user_id, doneType)
    await bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=kb
    )

    await callback.answer()

@dp.callback_query(F.data.startswith("register_doneGenres"))
async def get_genresRegister(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user_id = str(callback.from_user.id)

    data = await db_users.get_data_id(user_id)
    genres = data[0]["favoriteGenres"]
    await state.update_data(genres=genres)

    await db_users.update_favoriteGenres(user_id, genres)
    await callback.answer()

    content = f"Вы успешно зарегистрировались."
    builder = ReplyKeyboardBuilder()
    builder.button(text="Профиль")
    builder.button(text="Подобрать фильм")
    builder.adjust(2)
    kb = builder.as_markup(resize_keyboard=True)
    await bot.send_message(
        chat_id=chat_id,
        text=content,
        reply_markup=kb
    )
    await state.clear()

@dp.callback_query(F.data.startswith("changed_doneGenres"))
async def get_genresChanged(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user_id = str(callback.from_user.id)

    data = await db_users.get_data_id(user_id)
    genres = data[0]["favoriteGenres"]
    await state.update_data(genres=genres)

    await db_users.update_favoriteGenres(user_id, genres)
    await callback.answer()

    content = f"Ваши любимые жанры были успешно добавленны."
    builder = ReplyKeyboardBuilder()
    builder.button(text="Профиль")
    builder.button(text="Подобрать фильм")
    builder.adjust(2)
    kb = builder.as_markup(resize_keyboard=True)
    await bot.send_message(
        chat_id=chat_id,
        text=content,
        reply_markup=kb
    )
    await state.clear()

@dp.message(F.text.lower()=="профиль")
async def cmd_profil(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="Посмотреть любимые жанры")
    builder.button(text="Изменить любимые жанры")
    builder.button(text="Назад на главную")
    builder.adjust(2)
    kb = builder.as_markup(resize_keyboard=True)
    await message.answer(text="Ваш профиль:", reply_markup=kb)

@dp.message(F.text.lower()=="посмотреть любимые жанры")
async def cmd_showGenres(message: types.Message):
    user_id = message.from_user.id
    text = "Ваши любимые жанры:"
    data = await db_users.get_data_id(user_id)
    genres = data[0]["favoriteGenres"].split()
    for genre in genres:
        text += f"\n\t- {genre}"

    builder = ReplyKeyboardBuilder()
    builder.button(text="Изменить любимые жанры")
    builder.button(text="Назад на главную")
    builder.adjust(2)
    kb = builder.as_markup(resize_keyboard=True)
    await message.answer(text=text, reply_markup=kb)

@dp.message(F.text.lower()=="изменить любимые жанры")
async def cmd_steGenres(message: types.Message):
    user_id = message.from_user.id
    kb = await create_markup_Genres(user_id, "changed")
    await message.answer(text="Выберете ваши любимые жанры: ", reply_markup=kb)

@dp.message(F.text.lower()=="назад на главную")
async def cmd_back(message: types.Message):
    text = f"Вы вернулись на главную"
    builder = ReplyKeyboardBuilder()
    builder.button(text="Профиль")
    builder.button(text="Подобрать фильм")
    builder.adjust(2)
    kb = builder.as_markup(resize_keyboard=True)
    await message.answer(text=text, reply_markup=kb)

@dp.message(F.text.lower()=="подобрать фильм")
async def cmd_filmtest(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await bot.send_message(
        chat_id=chat_id,
        text="Для того чтобы выбрать вам идеальный фильм пройди мини-тест:"
    )

    content = ("1)🎭 Напиши свое настроение. Например: \n"
               "\t«хочу дождь и осень», \n"
               "\t«хочу смеяться», \n"
               "\t«хочу напряжения/адреналин», \n"
               "\t«плакать/чувственно»")
    await bot.send_message(
        chat_id=chat_id,
        text=content
    )
    await state.set_state(Test.mood)

@dp.message(Test.mood)
async def get_mood(message: types.Message, state: FSMContext):
    await state.update_data(mood=message.text)
    chat_id = message.chat.id
    content = ("2)👥 Напиши в какой компании ты планируешь смотреть фильм. Например: \n"
               "\t«один», \n"
               "\t«с партнёром», \n"
               "\t«с друзьями», \n"
               "\t«с детьми»")
    await bot.send_message(
        chat_id=chat_id,
        text=content
    )
    await state.set_state(Test.company)

@dp.message(Test.company)
async def get_mood(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    chat_id = message.chat.id
    content = "3)⏱️ Укажи какой по продолжительности ты бы хотел посмотреть фильм."
    btns = [
        [InlineKeyboardButton(text="<100мин", callback_data="get_timetest:<100мин")],
        [InlineKeyboardButton(text="100-140мин", callback_data="get_timetest:100-140мин")],
        [InlineKeyboardButton(text=">140мин", callback_data="get_timetest:>140мин")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=btns)

    await bot.send_message(
        chat_id=chat_id,
        text=content,
        reply_markup=kb
    )
    await state.set_state(Test.time)

@dp.callback_query(F.data.startswith("get_timetest"))
async def get_time(callback: types.CallbackQuery, state: FSMContext):
    btn_text = callback.data.split(":")[1]
    await state.update_data(time=btn_text)
    data = await state.get_data()
    mood = data["mood"]
    company = data["company"]
    time = data["time"]

    await callback.answer()

    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    content = ("Подбираем тебе фильмы...\n"
               "По данным:\n"
               f" - 🎭Настроение: {mood}\n"
               f" - 👥Компания: {company}\n"
               f" - ⏱️Время фильма: {time}")

    await db_storySearch.update_storyData(user_id, mood, company, time, "")
    await bot.send_message(
        chat_id=chat_id,
        text=content
    )
    await state.clear()

    await choosing_film(chat_id, user_id, (mood, company, time))


async def choosing_film(chat_id, user_id, data: tuple):
    mood, company, time = data

    user_data = await db_users.get_data_id(user_id)
    story_data = await db_storySearch.get_data_id(user_id)

    age = user_data[0]["age"]
    favoriteGenres = user_data[0]["favoriteGenres"]

    print("mood: ", mood)
    print("company: ", company)
    print("time: ", time)
    print("age: ", age)
    print("favoriteGenres: ", favoriteGenres)

    nameFilms = story_data[0]["lookingFilm"]
    response = await ai.requests(age, favoriteGenres, data, looking=nameFilms)

    nameFilms += " " + (await ai.get_filmName(response))
    await db_storySearch.update_storyData(user_id, mood, company, time, nameFilms)

    btns = [
        [InlineKeyboardButton(text="Показать еще", callback_data=f"see_more:{chat_id}:{user_id}")]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=btns)
    await bot.send_message(
        chat_id=chat_id,
        text=response,
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith("see_more"))
async def cmd_seeMore(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data.split(":")
    chat_id = data[1]
    user_id = data[2]
    data = await db_storySearch.get_data_id(user_id)
    mood = data[0]["mood"]
    company = data[0]["company"]
    time = data[0]["time"]
    lookingFilm = data[0]["lookingFilm"]

    await db_storySearch.update_storyData(user_id, mood, company, time, lookingFilm)

    content = ("Подбираем тебе фильмы...\n"
               "По данным:\n"
               f" - 🎭Настроение: {mood}\n"
               f" - 👥Компания: {company}\n"
               f" - ⏱️Время фильма: {time}")
    print("see more", content)

    await callback.answer()
    await bot.send_message(
        chat_id=chat_id,
        text="Подбираем новые фильмы..."
    )
    await choosing_film(chat_id, user_id, (mood, company, time))

async def main():
    await db_users.create_db()
    await db_storySearch.create_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())