from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_add_to_cart,
    orm_delete_from_cart,
    orm_get_banner,
    orm_get_categories,
    orm_get_products,
    orm_get_user_carts,
    orm_reduce_product_in_cart,
)
from kbds.inline import (
    get_products_btns,
    get_user_cart,
    get_user_catalog_btns,
    get_user_main_btns,
)

from utils.paginator import Paginator


async def main_menu(session, level, menu_name):
    # получаем меню, которое будет отправлено, menu_name - например, main
    banner = await orm_get_banner(session, menu_name)
    if banner is not None and banner.image:
        # получаем изображение меню и описание к изображению
        image = InputMediaPhoto(media=banner.image, caption=banner.description)
    else:
        image = None

    # формируем инлайн клавиатуру, передаем уровень меню
    kbds = get_user_main_btns(level=level)

    return image, kbds


async def catalog(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    if banner is not None and banner.image:
        image = InputMediaPhoto(media=banner.image, caption=banner.description)
    else:
        image = None

    categories = await orm_get_categories(session)
    kbds = get_user_catalog_btns(level=level, categories=categories)

    return image, kbds


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def products(session, level, category, page):
    products = await orm_get_products(session, category_id=category)
    if not products:
        return "🚫 Товары отсутствуют в данной категории", None
    paginator = Paginator(products, page=page)
    product = paginator.get_page()[0]

    unit = "л" if product.category.name == "Напитки" else "гр"

    image = InputMediaPhoto(
        media=product.image,
        caption=f"<strong>{product.name}\
                                </strong>\n{product.description}\nВес: {product.weight} {unit}\nЦена: {product.price} ₽\n<strong>Товар {paginator.page} из {paginator.pages}</strong>",
    )

    pagination_btns = pages(paginator)

    kbds = get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        product_id=product.id,
    )

    return image, kbds


async def carts(session, level, menu_name, page, user_id, product_id):
    if menu_name == "delete":
        await orm_delete_from_cart(session, user_id, product_id)
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await orm_reduce_product_in_cart(session, user_id, product_id)
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await orm_add_to_cart(session, user_id, product_id)

    carts = await orm_get_user_carts(session, user_id)

    if not carts:
        banner = await orm_get_banner(session, "cart")
        if banner is not None and banner.image:
            image = InputMediaPhoto(
                media=banner.image, caption=f"<strong>{banner.description}</strong>"
            )
        else:
            image = None

        kbds = get_user_cart(
            level=level,
            page=None,
            pagination_btns=None,
            product_id=None,
        )

    else:
        paginator = Paginator(carts, page=page)

        cart = paginator.get_page()[0]

        cart_price = round(cart.quantity * cart.product.price, 2)
        total_price = round(
            sum(cart.quantity * cart.product.price for cart in carts), 2
        )
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=f"Это Ваш товар <strong>№{paginator.page}</strong> из <strong>{paginator.pages}</strong> ⏬\n<strong>{cart.product.name}</strong>\n{cart.product.price} ₽ x {cart.quantity} = {cart_price} ₽\
                    \nОбщая стоимость товаров в корзине: {total_price} ₽",
        )

        pagination_btns = pages(paginator)

        kbds = get_user_cart(
            level=level,
            page=page,
            pagination_btns=pagination_btns,
            product_id=cart.product.id,
        )

    return image, kbds


async def get_menu_content(
        session: AsyncSession,
        level: int,
        menu_name: str,
        category: int | None = None,
        page: int | None = None,
        product_id: int | None = None,
        user_id: int | None = None,
):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)
    elif level == 3:
        return await carts(session, level, menu_name, page, user_id, product_id)
