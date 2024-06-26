import aiohttp
from token_tg import API_KEY

import json

import aiohttp
import asyncio

city_name = "Voronezh"
lat = 51.6605982
lon = 39.2005858


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ru') as resp:
            print(resp.status)
            print(json.loads(await resp.text()))


asyncio.run(main())
