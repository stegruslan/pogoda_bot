import json

import aiohttp

from database import session_factory, dp
from models import User, UserCity
from token_tg import API_KEY

from aiogram import F

from aiogram.types import Message


@dp.message(F.text == 'Узнать погоду')
async def handle_weather(message: Message):
    with session_factory() as session:
        user = session.query(User).filter(User.tg_id == message.from_user.id).first()
        if not user:
            return
        citys = session.query(UserCity).filter(UserCity.user_id == user.id).all()
        if not citys:
            await message.answer("У вас нет городов!")
        for city in citys:
            title = city.title
            lon, lat = city.lon, city.lat
            async with aiohttp.ClientSession() as request_session:
                async with request_session.get(
                        f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru') as resp:
                    data = json.loads(await resp.text())
                    description = data['weather'][0]['description']
                    temperature = data['main']['temp']
                    icon_name = data['weather'][0]['icon']
                    wind_name = data['wind']['speed']
                    pressure_name = data['main']['pressure']
                    feels_like_name = data['main']['feels_like']
                # async with request_session.get(
                #     f"https://openweathermap.org/img/wn/{icon_name}@4x.png"
                # ) as resp:
                #     with open(f"{icon_name}.png", "wb") as f:
                #         f.write(await resp.content.read())
                await message.answer_photo(caption=f"{title}:\n"
                                                   f"{description.title()}, температура : {temperature:,.0f} °C\n"
                                                   f"Скорость ветра : {wind_name:,.1f}м/c.\n"
                                                   f"Давление : {pressure_name} мм рт. ст.\n"
                                                   f"Ощущается как : {feels_like_name:,.0f} °C",
                                           photo=f"https://openweathermap.org/img/wn/{icon_name}@4x.png")
