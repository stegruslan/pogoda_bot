from datetime import datetime

from database import session_factory, dp
from models import User, menu_keyboard

from aiogram import html

from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    photo_url = "https://news-ru.gismeteo.st/2022/04/shutterstock_1902040933-640x360.jpg"
    await message.answer_photo(photo=photo_url, caption=f"Привет, {html.bold(message.from_user.full_name)}!\n"
                                                        f"Это бот для получения уведомлений о погоде.\n"
                                                        f"Чтобы начать пользоваться ботом добавьте ваш город.",
                               reply_markup=ReplyKeyboardMarkup(keyboard=menu_keyboard))
    with session_factory() as session:
        tg_user = message.from_user
        if session.query(User).filter(User.tg_id == tg_user.id).first():
            return
        user = User(tg_id=tg_user.id, username=tg_user.username, fullname=tg_user.full_name, created_at=datetime.now())
        session.add(user)
        session.commit()
