# наши модели для БД

from sqlalchemy import DateTime, Float, String, Text, func, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# создаем базовый класс для всех остальных
class Base(DeclarativeBase):
    # дата создания записи в БД, тип DateTime, func.now() - текущее время
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    # дата изменения записи в БД
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


# создаем таблицу для продуктов
class Product(Base):
    # название таблицы в БД
    __tablename__ = 'product'

    # поля (атрибуты), где указываем типы данных полей через Mapped
    # mapped_column - дополнительные свойства для атрибутов
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # максимальная длина 150 символов, nullable=False - не может быть пустым
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    # указываем тип Text вместо VarChar, чтобы хранить больший объем текста для описания
    description: Mapped[str] = mapped_column(Text)
    weight: Mapped[int] = mapped_column(Integer, nullable=False)  # Поле для веса товара (целое число)
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    image: Mapped[str] = mapped_column(String(150), nullable=False)

