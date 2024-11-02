# файл для query запросов

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from database.models import Product


# запрос для добавления продукта
async def orm_add_product(session: AsyncSession, data: dict):
    # создаем продукт, используя полученные данные с помощью машины состояний
    obj = Product(
        name=data["name"],
        description=data["description"],
        weight=int(data["weight"]),
        price=float(data["price"]),
        image=data["image"],
    )
    # добавляем объект к сессии
    session.add(obj)
    # сохраняем изменения данной сессии (после этого запись добавится в нашу БД)
    await session.commit()


# запрос для получения списка всех товаров
async def orm_get_products(session: AsyncSession):
    # выбираем все записи Product из БД
    query = select(Product)
    # выполняем наш запрос через session и сохраняем
    result = await session.execute(query)
    # возвращаем всё что получили (scalars, all - для нормального вида)
    return result.scalars().all()


# запрос для получения отдельного продукта
async def orm_get_product(session: AsyncSession, product_id: int):
    # получаем товар с переданным id
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    # возвращаем один объект
    return result.scalar()


# запрос для обновления информации о продукте
async def orm_update_product(session: AsyncSession, product_id: int, data):
    # обновляем данные у конкретного продукта
    query = update(Product).where(Product.id == product_id).values(
        name=data["name"],
        description=data["description"],
        weight=int(data["weight"]),
        price=float(data["price"]),
        image=data["image"], )
    await session.execute(query)
    # сохраняем изменения данной сессии (после этого запись изменится в нашей БД)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    # удаляем конкретный продукт
    query = delete(Product).where(Product.id == product_id)
    # выполняем запрос
    await session.execute(query)
    # сохраняем изменения в БД
    await session.commit()
