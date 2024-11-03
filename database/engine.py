# запуск движка ORM

import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# наши импорты
from database.models import Base
from database.orm_query import orm_add_banner_description, orm_create_categories
from common.texts_for_db import categories, description_for_info_pages

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
    # открываем сессию и записываем категории при старте бота и описание для страниц баннера
    async with session_maker() as session:
        await orm_create_categories(session, categories)
        await orm_add_banner_description(session, description_for_info_pages)


# функция для сброса таблиц в БД
async def drop_db():
    async with engine.begin() as conn:
        # drop_all - удалить все наши таблицы из models
        await conn.run_sync(Base.metadata.drop_all)
