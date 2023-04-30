from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
import httplib2
import pandas as pd
import requests
import os

from database.db import *
from parser import *

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
def get_user(telegram_user = None, tg_id : str = None) -> User:
    if telegram_user:
        return User.get(tg_id=str(telegram_user.id))
    if tg_id:
        return User.get(tg_id=tg_id)

@db_session
def get_users() -> list:
    return select(u for u in User)[:]
        
@db_session()
def update_user(
    tg_id : str, 
    username : str = None,
    first_name : str = None,
    last_name : str = None,
    phone : str = None,
    address : str = None,
    promocode : str = None,
    sizes : str = None,
    shoe_sizes : str = None,
    brands : str = None,
    prices : str = None,
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
    if promocode:
        user_to_update.promocode = Promocode.get(name=promocode)
    if is_banned:
        user_to_update.is_banned = is_banned
    if sizes:
        user_to_update.sizes = sizes
    if shoe_sizes:
        user_to_update.shoe_sizes = shoe_sizes
    if brands:
        user_to_update.brands = brands
    if prices:
        user_to_update.prices = prices
    if is_banned == False:
        user_to_update.is_banned = is_banned
    if last_usage:
        user_to_update.last_usage = datetime.now()
    return user_to_update

# Cart
@db_session()
def add_to_cart(tg_id : str, product_id : int):
    if not Cart.exists(user=User.get(tg_id=tg_id), product=Product[product_id].article):
        return Cart(user=User.get(tg_id=tg_id), product=Product[product_id].article)

@db_session()
def get_cart(tg_id : str):
    return [Product.get(article=str(article)) for article in select(cart.product for cart in Cart if cart.user == User.get(tg_id=tg_id))[:]]

@db_session()
def delete_from_cart(tg_id : str, product_id : int):
    cart_to_delete = Cart.get(user=User.get(tg_id=tg_id), product=Product[product_id].article)
    cart_to_delete.delete()

@db_session()
def cart_exists(tg_id : str, product_id : int):
    return Cart.exists(user=User.get(tg_id=tg_id), product=Product[product_id].article)

# Product
@db_session()
def update_product(
    product_id : int,
    category : Category = None,
    #catalog : Catalog = None,
    name : str = None, 
    description : str = None, 
    price : float = None, 
    sizes : str = None,
    image : str = None,
    several_images : bool = False,
    article : str = None,
    deleted : bool = None,
    edited : bool = None) -> Product:
    product_to_upd = Product[product_id]
    if name:
        product_to_upd.name = name
    if category:
        product_to_upd.category = category
    #if catalog:
    #    product_to_upd.catalog = catalog
    if description:
        product_to_upd.description = description
    if price:
        product_to_upd.price = price
    if sizes:
        product_to_upd.sizes = sizes
    if image and not several_images:
        print('ok')
        product_to_upd.image = image
    if image and several_images:
        product_to_upd.image += '\n' + image
    if deleted or deleted == False:
        product_to_upd.deleted = deleted
    if edited or edited == False:
        product_to_upd.edited = edited
    if article:
        product_to_upd.article = article

    return product_to_upd

@db_session()
def create_product(
    name : str, 
    category : str,
    subcategory : str,
    description : str = None,
    sizes : str = None, 
    price : float = None, 
    image : str = None,
    article : str = None) -> Product:
    
    if category_exists(name=category):
        category = Category.get(name=category)
    else:
        category = Category(name=category)
    if subcategory:
        if subcategory_exists(name=subcategory, category=category.name):
            subcategory = SubCategory.get(name=subcategory, category=category)
        else:
            subcategory = SubCategory(name=subcategory, category=category)

    product = Product(
        name=name,
        category=category,
        subcategory=subcategory,
        description=description,
        sizes=sizes,
        price=price,
        image=image,
        article=article
    )
    return product

@db_session()
def create_products(items):
    for item in items:
        if category_exists(name=category):
            category = Category.get(name=item[1])
        else:
            category = Category(name=item[1])
        if subcategory:
            if subcategory_exists(name=item[2]):
                subcategory = SubCategory.get(name=item[2])
            else:
                subcategory = SubCategory(name=item[2], category=item[1])
        Product(
        name=item[0],
        category=category,
        subcategory=subcategory,
        #catalog=Catalog.get(phone=item[3]),
        description=item[4],
        price=item[5],
        image=item[6]
    )

@db_session()
def get_categories():
    return select(p.category for p in Product)[:]

@db_session()
def get_product(
    id : int = None, 
    #catalog : str = None, 
    category_id : int = None, 
    subcategory_id : int = None, 
    sizes : str = None, 
    prices : str = None, 
    sort : str = None,
    article : str = None):
    if id:
        return Product[id]
    #if catalog:
    #    return select(p for p in Product if p.catalog.phone == catalog)[:]
    elif category_id and not subcategory_id:
        return select(p for p in Product if p.category.id == category_id)[:]
    elif category_id and subcategory_id and not sizes and not prices:
        if sort == 'n':
            return select(p for p in Product if p.category.id == category_id and p.subcategory.id == subcategory_id)[:]
        elif sort == 'u':
            return  Product.select(lambda p: p.category.id == category_id and p.subcategory.id == subcategory_id).order_by(Product.price)[:]
        elif sort == 'd':
            return  Product.select(lambda p: p.category.id == category_id and p.subcategory.id == subcategory_id).order_by(desc(Product.price))[:]
         
    elif category_id and subcategory_id and (sizes or prices):
        if sort == 'n':
            products = select(p for p in Product if p.subcategory.id == subcategory_id)[:]
        elif sort == 'u':
            products = Product.select(lambda p: p.subcategory.id == subcategory_id).order_by(Product.price)[:]
        elif sort == 'd':
            products = Product.select(lambda p: p.subcategory.id == subcategory_id).order_by(desc(Product.price))[:]
        filter_products = []
        for prod in products:
            if sizes and not prices:
                if len(list(set(sizes.split("-")) & set(str(prod.sizes).split(', ')))) > 0:
                    filter_products.append(prod)
            elif prices and not sizes:
                if '1' in prices:
                    if prod.price <= 5000:
                        filter_products.append(prod)
                if '2' in prices:
                    if prod.price >= 5000 and prod.price <= 10000:
                        filter_products.append(prod)
                if '3' in prices:
                    if prod.price >= 10000 and prod.price <= 20000:
                        filter_products.append(prod)
                if '4' in prices:
                    if prod.price >= 20000 and prod.price <= 30000:
                        filter_products.append(prod)
                if '5' in prices:
                    if prod.price >= 30000 and prod.price <= 40000:
                        filter_products.append(prod)
                if '6' in prices:
                    if prod.price >= 40000:
                        filter_products.append(prod)
            elif sizes and prices:
                if len(list(set(sizes.split("-")) & set(str(prod.sizes).split(', ')))) > 0:
                    if '1' in prices:
                        if prod.price <= 10000:
                            filter_products.append(prod)
                    if '2' in prices:
                        if prod.price >= 10000 and prod.price <= 20000:
                            filter_products.append(prod)
                    if '3' in prices:
                        if prod.price >= 20000 and prod.price <= 50000:
                            filter_products.append(prod)
                    if '4' in prices:
                        if prod.price >= 50000:
                            filter_products.append(prod)
                    
        return filter_products
    if article:
        return Product.get(article=article)
        
        

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

# удаление только для юзеров (админам остаются видны)
@db_session()
def del_product(id : int, forever : bool = False):
    product_to_delete = Product[id]
    if forever:
        return product_to_delete.delete()
    else:
        return product_to_delete.deleted == True

@db_session()
def del_products(catalog : str = None, category : str = None, subcategory : str = None):
    #if catalog:
    #    products_to_delete = select(p for p in Product if p.catalog == Catalog.get(phone=catalog) and not p.deleted and not p.edited)[:]
    #    for product in  products_to_delete:
    #        product.delete()
    if category:
        products_to_delete = select(p for p in Product if p.category == Category.get(name=category))[:]
        for product in  products_to_delete:
            product.delete()
    if subcategory:
        products_to_delete = select(p for p in Product if p.subcategory == SubCategory.get(name=subcategory) and not p.deleted and not p.edited)[:]
        for product in  products_to_delete:
            product.delete()




# Category
@db_session()
def create_category(name : str, margin : int, custom : bool = False):
    category = Category(name=name)
    if custom:
        category.custom = custom
    if margin:
        category.margin = margin
    

@db_session()
def get_category(id : int = None, name : str = None):
    if id:
        return Category[id]
    if name:
        return Category.get(name=name)
    else:
        return select(c for c in Category)[:]

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
def subcategory_exists(name : str, category : str):
    return SubCategory.exists(name=name, category=Category.get(name=category))


# Promocode
@db_session()
def create_promocode(name : str, discount : int):
    return Promocode(name=name, discount=discount)

@db_session()
def get_promocode(id : int = None, name : str = None, tg_id : str = None, users : bool = False, categories : bool = False):
    if id:
        if users:
            return select(u for u in Promocode[id].users)[:]
        if categories:
            return select(u for u in Promocode[id].categories)[:]
        else:
            return Promocode[id]
    if name:
        return Promocode.get(name=name)
    if tg_id:
        return select(p for p in Promocode if User.get(tg_id=tg_id) in p.users)
    else:
        return select(p for p in Promocode)[:]
    
@db_session()
def update_promocode(name : str, discount : int = None, categories : list = None, tg_id : str = None):
    promocode_to_update = Promocode.get(name=name)
    if discount:
        promocode_to_update.discount = discount
    if categories:
        categories_obj = [get_category(id=cat) for cat in categories]
        promocode_to_update.categories = categories_obj
    if tg_id:
        user = User.get(tg_id=tg_id)
        promocode_to_update.users += user
    return promocode_to_update

@db_session()
def delete_promocode(id : int = None, name : str = None):
    if id:
        Promocode[id].delete()
    if name:
        Promocode.get(name=name).delete()

@db_session()
def promocode_exists(name : str):
    return Promocode.exists(name=name)

@db_session()
def get_user_promocode(tg_id : str):
    try:
        return User.get(tg_id=tg_id).promocode.id
    except:
        return False

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