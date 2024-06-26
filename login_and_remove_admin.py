from aiogram.fsm.context import FSMContext

from database import session_factory, dp
from models import User, AdminSign
from token_tg import ADMIN_PASSWORD

from aiogram.filters import Command
from aiogram.types import Message


@dp.message(AdminSign.password)
async def handle_password(message: Message, state: FSMContext):
    if ADMIN_PASSWORD == message.text:
        with session_factory() as session:
            user = session.query(User).filter(User.tg_id == message.from_user.id).first()
            if user:
                user.is_admin = True
                session.commit()
                await message.answer("Вы теперь администратор!")
    else:
        await message.answer("Неверный пароль!")
    await state.clear()

    @dp.message(Command('remove_admin'))
    async def handle_rem_admin(message: Message):
        with session_factory() as session:
            user = session.query(User).filter(User.tg_id == message.from_user.id).first()
            if user:
                if user.is_admin:
                    user.is_admin = False
                    session.commit()
                    await message.answer("Вы больше не администратор!")


@dp.message(Command('admin'))
async def admin_handler(message: Message, state: FSMContext) -> None:
    with session_factory() as session:
        user = session.query(User).filter(User.tg_id == message.from_user.id).first()
        if not user:
            return
        if user.is_admin:
            await message.answer("Вы уже администратор!")
            return
        await state.set_state(AdminSign.password)
        await message.answer("Введите админский пароль!")
