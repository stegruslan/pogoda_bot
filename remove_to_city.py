from database import session_factory, dp
from models import User, UserCity, DeleteCityCallback

from aiogram import F

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery


@dp.message(F.text == 'Удалить город')
async def handle_remove_city(message: Message):
    with session_factory() as session:
        user = session.query(User).filter(User.tg_id == message.from_user.id).first()
        user_citys = session.query(UserCity).filter(UserCity.user_id == user.id).all()
        if not user_citys:
            await message.answer(text='У вас нет городов!')
            return
        delete_keyboard = [
            [InlineKeyboardButton(text=city.title,
                                  callback_data=DeleteCityCallback(title=city.title).pack())]
            for city in user_citys
        ]
        delete_keyboard.append([InlineKeyboardButton(text='Закрыть',
                                                     callback_data=DeleteCityCallback(title='Закрыть').pack())])
        await message.answer(text="Выберите город для удаления!",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=delete_keyboard))


@dp.callback_query(DeleteCityCallback.filter(F.title != ''))
async def handle_delete_city_callback(query: CallbackQuery, callback_data: DeleteCityCallback):
    with session_factory() as session:
        if callback_data.title == 'Закрыть':
            await query.message.delete()
            return
        user = session.query(User).filter(User.tg_id == query.from_user.id).first()
        if not user:
            return
        title = callback_data.title
        city = session.query(UserCity).filter(UserCity.user_id == user.id).filter(UserCity.title == title).first()
        if city:
            session.delete(city)
            session.commit()
        markup = query.message.reply_markup
        if markup:
            new_markup = [
                button
                for button in
                markup.inline_keyboard
                if button[0].text != title
            ]
            await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=new_markup))
