import asyncio
import functools
import json
import logging
import sys

from aiogram.client.session import aiohttp
from celery import Celery
from celery.schedules import crontab

import start_message
import add_city
import login_and_remove_admin
import remove_to_city
import to_know_weather
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from database import dp, session_factory, celery
from models import UserCity
from token_tg import BOT_TOKEN, API_KEY


def async_to_sync(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapped


@celery.task
@async_to_sync
async def handle_weather_for_city(city: dict):
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    title = city['title']
    lon, lat = city['lon'], city['lat']
    async with aiohttp.ClientSession() as request_session:
        async with request_session.get(
                f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru') as resp:
            data = json.loads(await resp.text())
            description = data['weather'][0]['description']
            temperature = data['main']['temp']
            icon_name = data['weather'][0]['icon']
    await bot.send_photo(caption=f"{title}:\n"
                                 f"{description.title()}, температура - {temperature}C\n",
                         photo=f"https://openweathermap.org/img/wn/{icon_name}@4x.png", chat_id=city['chat_id'])


@celery.task
@async_to_sync
async def handle_citys_from_database():
    with session_factory() as session:
        citys = session.query(UserCity).all()
        for city in citys:
            handle_weather_for_city.apply_async(
                args=[{"chat_id": city.chat_id, "lat": city.lat, "lon": city.lon, "title": city.title}])


celery.conf.beat_schedule = {
    'add-every-monday-morning': {
        'task': 'tasks.add',
        'schedule': crontab(hour='23', minute='49', day_of_week='*'),
        'args': (16, 16),
    }}


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    with session_factory() as session:
        city = session.query(UserCity).first()
        if city:
            handle_weather_for_city.apply_async(
                args=[{"chat_id": city.chat_id, "lat": city.lat, "lon": city.lon, "title": city.title}])
        else:
            logging.info("No city found in the database.")
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
