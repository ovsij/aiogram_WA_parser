from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
import httplib2
import pandas as pd
import requests
import os

from database.db import *
from parser.parser import *

# User
@db_session
def register_user(telegram_user) -> User:
    if not User.exists(tg_id = str(telegram_user.id)):
        user = User(
            tg_id=str(telegram_user.id), 
            username=telegram_user.username, 
            first_name=telegram_user.first_name, 
            last_name=telegram_user.last_name)
        flush()
        return user
    else:
        print(f'User {telegram_user.id} exists')

@db_session
def get_user(telegram_user) -> User:
    return User.get(tg_id=str(telegram_user.id))

@db_session
def get_users() -> list:
    return select(int(u.tg_id) for u in User)[:]
        
@db_session()
def update_user(
    tg_id : str, 
    username : str = None,
    first_name : str = None,
    last_name : str = None,
    phone : str = None,
    address : str = None,
    last_usage : bool = None,
    is_banned : bool = None
    ) -> User:

    user_to_update = User.get(tg_id = tg_id)
    if username:
        user_to_update.username = username
    if first_name:
        user_to_update.first_name = first_name
    if last_name:
        user_to_update.last_name = last_name
    if phone:
        user_to_update.phone = phone
    if address:
        user_to_update.address = address
    if is_banned:
        user_to_update.is_banned = is_banned
    if is_banned == False:
        user_to_update.is_banned = is_banned
    if last_usage:
        user_to_update.last_usage = datetime.now()
    return user_to_update

# Product
@db_session()
def update_product(
    product : Product,
    category : Category,
    catalog : Catalog,
    name : str = None, 
    description : str = None, 
    price : float = None, 
    image : str = None) -> Product:
    product_to_upd = product
    if name:
        product_to_upd.name = name
    if category:
        product_to_upd.category = category
    if catalog:
        product_to_upd.catalog = catalog
    if description:
        product_to_upd.description = description
    if price:
        product_to_upd.price = price
    if image:
        product_to_upd.image = image

    return product_to_upd

@db_session()
def create_product(
    name : str, 
    category : str,
    subcategory : str,
    catalog : str, 
    description : str = None, 
    price : float = None, 
    image : str = None) -> Product:
    #if Product.exists(name = name, description = description, price = price):
    #    Product.get(name = name, description = description, price = price).delete()
    if category_exists(name=category):
        category = Category.get(name=category)
    else:
        category = Category(name=category, catalog=Catalog.get(phone=catalog))
    if subcategory:
        if subcategory_exists(name=subcategory):
            subcategory = SubCategory.get(name=subcategory)
        else:
            subcategory = SubCategory(name=subcategory, category=category)

    product = Product(
        name=name,
        category=category,
        subcategory=subcategory,
        catalog=Catalog.get(phone=catalog),
        description=description,
        price=price,
        image=image
    )
    return product

@db_session()
def create_products(items):
    for item in items:
        if category_exists(name=category):
            category = Category.get(name=item[1])
        else:
            category = Category(name=item[1], catalog=Catalog.get(phone=item[3]))
        if subcategory:
            if subcategory_exists(name=item[2]):
                subcategory = SubCategory.get(name=item[2])
            else:
                subcategory = SubCategory(name=item[2], category=item[1])
        Product(
        name=item[0],
        category=category,
        subcategory=subcategory,
        catalog=Catalog.get(phone=item[3]),
        description=item[4],
        price=item[5],
        image=item[6]
    )

@db_session()
def get_categories():
    return select(p.category for p in Product)[:]

@db_session()
def get_product(id : int = None, category_id : int = None, subcategory_id : int = None):
    if id:
        return Product[id]
    if category_id and not subcategory_id:
        return select(p for p in Product if p.category.id == category_id)[:]
    if category_id and subcategory_id:
        return select(p for p in Product if p.category.id == category_id and p.subcategory.id == subcategory_id)[:]

@db_session()
def get_products_by_category(category : int):
    return select(p for p in Product if p.category.id == category)[:]


@db_session()
def get_image(prod_id : int):
    return Product[prod_id].image    

@db_session()
def get_last_id():
    try:
        return max(select(p.id for p in Product)[:]) 
    except ValueError:
        print('Список продуктов пуст')
        return 0

@db_session()
def del_products(catalog : str = None, category : str = None, subcategory : str = None):
    if catalog:
        products_to_delete = select(p for p in Product if p.catalog == Catalog.get(phone=catalog))[:]
        for product in  products_to_delete:
            product.delete()
            #SubCategory[product.subcategory.id].delete()
    if category:
        products_to_delete = select(p for p in Product if p.category == Category.get(name=category))[:]
        for product in  products_to_delete:
            product.delete()
    if subcategory:
        products_to_delete = select(p for p in Product if p.subcategory == SubCategory.get(name=subcategory))[:]
        for product in  products_to_delete:
            product.delete()




# Category
@db_session()
def create_category(name : str, catalog : str):
    catalog = Catalog.get(phone=catalog)
    return Category(name=name, catalog=catalog)

@db_session()
def get_category(id : int = None, name : str = None, catalog_id : Catalog = None):
    if id:
        return Category[id]
    if name:
        return Category.get(name=name)
    if catalog_id:
        return Category.get(id=catalog_id)

@db_session()
def delete_category(id : int = None, name : str = None):
    if id:
        Category[id].delete()
    if name:
        Category.get(name=name).delete()

@db_session()
def category_exists(name : str):
    return Category.exists(name=name)

#SubCategory
@db_session()
def create_subcategory(name : str, category : str):
    return SubCategory(name=name, category=Category.get(name=category))

@db_session()
def get_subcategory(id : int = None, name : str = None, category_id : int = None):
    if id:
        return SubCategory[id]
    if name:
        return SubCategory.get(name=name)
    if category_id:
        return select(sc for sc in SubCategory if sc.category == Category[category_id])[:]

@db_session()
def delete_subcategory(id : int = None, name : str = None):
    if id:
        SubCategory[id].delete()
    if name:
        SubCategory.get(name=name).delete()

@db_session()
def subcategory_exists(name : str):
    return SubCategory.exists(name=name)

# Catalog
@db_session()
def create_catalog(phone : str, link: str):
    return Catalog(phone=phone, link=link)

@db_session()
def get_catalog(id : int = None, phone : str = None):
    if id:
        return Catalog[id]
    if phone:
        return Catalog.get(phone=phone)
    
@db_session()
def get_catalogs():
    return select(c for c in Catalog)[:]


@db_session()
def update_catalog(phone : str, margin : int):
    catalog_to_update = Catalog.get(phone=phone)
    catalog_to_update.margin = margin
    return catalog_to_update

@db_session()
def delete_catalog(id : int = None, phone : str = None):
    if id:
        Catalog[id].delete()
    if phone:
        Catalog.get(phone=phone).delete()

@db_session()
def catalog_exists(phone : str):
    return Catalog.exists(phone=phone)




#Создание демонстрационной базы данных
@db_session()
def update_catalog_info():
    df = get_catalog('https://web.whatsapp.com/catalog/393427688947')
    print(df)
    """
    try:
        os.mkdir(f'database/images/{tg_id}')
    except FileExistsError:
        pass

    for i in range(len(df)):
        if not Product.exists(name=df.iloc[i]['Наименование']):

            # создаем продукт
            product = create_product(
                name=str(df.iloc[i]['Наименование']),
                description=str(df.iloc[i]['Описание']),
                price=float(df.iloc[i]['Цена']),
                image=f"database/images/{df.iloc[i]['Наименование']}.jpeg",
                )
            
            if Category.exists(name=str(df.iloc[i]['Категория'])):
                update_product(product=product, category=Category.get(name=str(df.iloc[i]['Категория'])))
            else:
                update_product(product=product, category=Category(name=str(df.iloc[i]['Категория'])))       
"""