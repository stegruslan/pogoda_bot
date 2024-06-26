from datetime import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, relationship


class BaseORM(DeclarativeBase):
    __abstract__ = True


class User(BaseORM):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[str | None]
    fullname: Mapped[str]
    created_at: Mapped[datetime]
    is_admin: Mapped[bool] = mapped_column(default=False)
    citys: Mapped[list["UserCity"]] = relationship(back_populates='user')


class UserCity(BaseORM):
    __tablename__ = 'citys'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    lon: Mapped[float]
    lat: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship(back_populates='citys')
    chat_id: Mapped[int]


class AdminSign(StatesGroup):
    password = State()


class AddCityStates(StatesGroup):
    title = State()


menu_keyboard = [
    [KeyboardButton(text="Узнать погоду")],
    [KeyboardButton(text="Добавить город")],
    [KeyboardButton(text="Удалить город")],
]


class DeleteCityCallback(CallbackData, prefix='delete_city'):
    title: str
