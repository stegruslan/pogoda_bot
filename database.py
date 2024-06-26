from aiogram import Dispatcher
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import BaseORM


def db_setup():
    db_engine = create_engine("sqlite:///db.sqlite3")
    db_session_factory = sessionmaker(bind=db_engine)
    with db_session_factory() as session:
        BaseORM.metadata.create_all(db_engine)
        session.commit()
    return db_engine, db_session_factory


engine, session_factory = db_setup()

dp = Dispatcher()
celery = Celery('main', broker='pyamqp://guest:guest@localhost:5672/')