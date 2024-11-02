# запуск движка ORM

import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base

# from .env file:
# DB_URL=postgresql+asyncpg://login:password@localhost:5432/db_name

# создаем объект движка, выводим все события в терминал через echo
engine = create_async_engine(os.getenv('DB_URL'), echo=True)
# переменная для создания сессий, expire_on_commit = False, чтобы воспользоваться сессией после коммита
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# функция для создания таблиц в БД
async def create_db():
    async with engine.begin() as conn:
        # create_all - создать все наши таблицы из models
        await conn.run_sync(Base.metadata.create_all)


# функция для сброса таблиц в БД
async def drop_db():
    async with engine.begin() as conn:
        # drop_all - сбросить все наши таблицы из models
        await conn.run_sync(Base.metadata.drop_all)
