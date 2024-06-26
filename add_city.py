import json

import aiohttp
from aiogram import F

from aiogram.fsm.context import FSMContext

from database import session_factory, dp
from models import User, UserCity, AddCityStates
from token_tg import API_KEY

from aiogram.types import Message


@dp.message(AddCityStates.title)
async def handle_add_city_title(message: Message, state: FSMContext):
    with session_factory() as session:
        user = session.query(User).filter(User.tg_id == message.from_user.id).first()
        if not user:
            return
        title = message.text
        async with aiohttp.ClientSession() as request_session:
            async with request_session.get(
                    f'http://api.openweathermap.org/geo/1.0/direct?q={title}&limit=1&appid={API_KEY}&lang=ru') as resp:
                data = json.loads(await resp.text())
        if not data:
            await message.answer("Город не найден!")
            return
        lon = data[0]['lon']
        lat = data[0]['lat']
        ru_title = data[0]['local_names']['ru']
        city = session.query(UserCity).filter(UserCity.user_id == user.id).filter(UserCity.title == ru_title).first()
        if city:
            await message.answer("Этот город уже добавлен!")
            await state.clear()
            return
        city = UserCity(user_id=user.id, title=ru_title, lon=lon, lat=lat, chat_id=message.chat.id)
        session.add(city)
        session.commit()
        await message.answer(f"Город {ru_title} добавлен!")
        await state.clear()


@dp.message(F.text == 'Добавить город')
async def handle_add_city(message: Message, state: FSMContext):
    await state.set_state(AddCityStates.title)
    await message.answer("Введите название города.")