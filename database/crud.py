from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
import difflib
import httplib2
import pandas as pd
import requests
import os
import logging

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
    is_banned : bool = None,
    state : bool = None
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
        user_to_update.promocode += Promocode.get(name=promocode)
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
    if state:
        user_to_update.state = state
    return user_to_update

# Cart
@db_session()
def add_to_cart(tg_id : str, product_id : int, sizes : str):
    if not Cart.exists(user=User.get(tg_id=tg_id), product=Product[product_id]):
        return Cart(user=User.get(tg_id=tg_id), product=Product[product_id], sizes=sizes)
    else:
        cart_to_upgrade = Cart.get(user=User.get(tg_id=tg_id), product=Product[product_id])
        cart_to_upgrade.sizes = sizes
        return cart_to_upgrade

@db_session()
def get_cart(tg_id : str):
    return select(cart.product for cart in Cart if cart.user == User.get(tg_id=tg_id))[:]

@db_session()
def delete_from_cart(tg_id : str, product_id : int):
    cart_to_delete = Cart.get(user=User.get(tg_id=tg_id), product=Product[product_id])
    cart_to_delete.delete()

@db_session()
def cart_exists(tg_id : str, product_id : int):
    return Cart.exists(user=User.get(tg_id=tg_id), product=Product[product_id])

# Product
@db_session()
def update_product(
    product_id : int,
    category : str = None,
    name : str = None, 
    description : str = None, 
    price : float = None, 
    sizes : str = None,
    image : str = None,
    several_images : bool = False,
    article : str = None,
    deleted : bool = None,
    edited : bool = None,
    url : str = None) -> Product:
    product_to_upd = Product[product_id]
    if category:
        if category_exists(name=category):
            new_category = Category.get(name=category)
        else:
            new_category = Category(name=category,  phone=category.lower(), margin=30)
    if name:
        product_to_upd.name = name
    if category:
        product_to_upd.category = new_category
    if description:
        product_to_upd.description = description
    if price:
        product_to_upd.price = price
    if sizes:
        product_to_upd.sizes = sizes
    if image and not several_images:
        product_to_upd.image = image
    if image and several_images:
        product_to_upd.image += '\n' + image
    if deleted or deleted == False:
        product_to_upd.deleted = deleted
    if edited or edited == False:
        product_to_upd.edited = edited
    if article:
        product_to_upd.article = article
    if url:
        product_to_upd.url = url

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
    article : str = None,
    url : str = None) -> Product:
    
    if category_exists(name=category):
        category = Category.get(name=category)
    else:
        category = Category(name=category,  phone=category.lower(), margin=30)
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
        article=article,
        url=url
    )
    return product

@db_session()
async def create_products(category : str, subcategory : str, items : list):
    
    print('add')
    # удаляем старые товары
    all_articles = [item[5] for item in items]
    category_ = Category.get(name=category)
    subcategory_ = SubCategory.get(name=subcategory, category=category_)
    # Разослать юзерам что товар из их корзины удален
    users = get_users()
    for user in users:
        try:
            #print(user.username)
            cart = get_cart(user.tg_id)
            #print(cart)
            for product in cart:
                #print(product)
                if product.article not in all_articles and product.subcategory.id == subcategory_.id:
                    #print(product.article)
                    await bot.send_message(user.tg_id, f'К сожалению, товар {product.name} ({product.category.name}) из вашей корзины закончился')
        except:
            continue

    all_images = []
    for product in get_product(category_id=category_.id, subcategory_id=subcategory_.id, sort='n'):
        if product.article not in all_articles:
            #logging.info('delete')
            product.delete()
        else:
            all_images += product.image.split('\n')
   
    for root, dirs, files in os.walk(f"database/images/{category}/{subcategory}/"):
        for filename in files:
            if f"database/images/{category}/{subcategory}/{filename}" not in all_images:
                pass
                #logging.info('delete image')
                #os.remove(f"database/images/{category}/{subcategory}/{filename}")
    # создаем новые/обновляем товары
    all_articles = []
    for item in items:
        try:
            if not crud.product_exists(article=item[5], subcategory_id=subcategory_.id):
                prod = crud.create_product(
                name=item[0],
                category=category,
                subcategory=subcategory,
                description=item[1],
                sizes=item[4],
                price=item[2],
                image=item[3],
                article=item[5],
                url=item[6])
                commit()
                #logging.info(f'create {prod}')
            else:
                prod = crud.get_product(article=item[5], subcategory_id = subcategory_.id)
                if not prod.deleted and not prod.edited:
                    crud.update_product(
                        product_id=prod.id,
                        name=item[0],
                        description=item[1],
                        sizes=item[4],
                        price=item[2],
                        image=item[3],
                        article=item[5],
                        url=item[6]
                    )
                    commit()
            logging.info(f'{prod} {prod.name}')
        except Exception as ex:
            logging.warning(f'{category} db - {ex}')

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
    article : str = None,
    search : str = None):
    if id:
        return Product[id]
    #if catalog:
    #    return select(p for p in Product if p.catalog.phone == catalog)[:]
    elif category_id and search:
        all_products = select(p for p in Product if p.category.id == category_id and search.lower() in p.name.lower())[:]
        #products = []
        #for p in all_products:
        #    matcher = difflib.SequenceMatcher(None, search.lower(), p.name.lower())
        #    if matcher.ratio() >= 0.15:
        #        products.append(p)
        return all_products
    elif category_id and not subcategory_id:
        return select(p for p in Product if p.category.id == category_id)[:]
    elif category_id and subcategory_id and not sizes and not prices:
        if sort == 'n':
            if SubCategory[subcategory_id].childSubCategory:
                return select(p for p in Product if p.category.id == category_id and p.subcategory.parentSubCategory.id == subcategory_id)[:]
            else:
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
        subcategory = SubCategory[subcategory_id]
        return Product.get(article=article, subcategory=subcategory)

@db_session()     
def product_exists(article : str, subcategory_id : int):
    return Product.exists(subcategory = SubCategory[subcategory_id], article=article)

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
    
    products_to_delete = select(p for p in Product if p.subcategory == SubCategory.get(name=subcategory, category=Category.get(name=category)) and not p.deleted and not p.edited)[:]
    for product in  products_to_delete:
        product.delete()


# metaCategory
@db_session()
def create_metacategory(name : str):
    return MetaCategory(name=name)
    
@db_session()
def get_metacategory(id : int = None, name : str = None):
    if id:
        return MetaCategory[id]
    if name:
        if MetaCategory.exists(name=name):
            return MetaCategory.get(name=name)
        else:
            return MetaCategory(name=name)
    else:
        return select(mc for mc in MetaCategory)[:]

@db_session()
def delete_metacategory(id : int = None, name : str = None):
    if id:
        MetaCategory[id].delete()
    if name:
        MetaCategory.get(name=name).delete()

@db_session()
def metacategory_exists(name : str):
    return MetaCategory.exists(name=name)

# Category
@db_session()
def create_category(meta : int, name : str, margin : int, custom : bool = False, phone=None):
    category = Category(name=name, metaCategory=meta)
    if custom:
        category.custom = custom
    if margin:
        category.margin = margin
    if phone:
        category.phone = phone

@db_session()
def get_category(id : int = None, name : str = None, metacategory : int = None):
    if id:
        return Category[id]
    if name and metacategory:
        if Category.exists(name=name):
            return Category.get(name=name)
        else:
            return Category(name=name, phone=name.lower(), margin=30, metaCategory=metacategory)
    if name and not metacategory:
        return Category.get(name=name)
    if metacategory and not name:
        return select(c for c in Category if c.metaCategory.id == metacategory)[:]
    else:
        return select(c for c in Category)[:]

@db_session()
def delete_category(id : int = None, name : str = None, phone : str = None):
    if id:
        Category[id].delete()
    if name:
        Category.get(name=name).delete()
    if phone:
        Category.get(phone=phone).delete()

@db_session()
def category_exists(name : str, phone : str = None):
    if name and phone:
        if not Category.exists(name=name):
            return Category.exists(phone=phone)
        else:
            return True
    else:
        return Category.exists(name=name)

@db_session()
def update_category(phone : str, margin : int):
    cat_to_update = Category.get(phone=phone)
    cat_to_update.margin = margin


#SubCategory
@db_session()
def create_subcategory(name : str, category : str, parent_subcategory : int = None, level : int = None):
    if Category.exists(name=category):
        category = Category.get(name=category)
    else:
        category = Category(name=category, phone=category.lower(), margin=30)
    if not parent_subcategory:
        return SubCategory(name=name, category=category)
    else:
        return SubCategory(name=name, category=category, parentSubCategory=parent_subcategory, level=level)

@db_session()
def get_subcategory(id : int = None, name : str = None, category_id : int = None, level : int = None, parent_subcategory : int = None):
    if id:
        return SubCategory[id]
    if name:
        return SubCategory.get(name=name, category=Category[category_id])
    if category_id and not level:
        return select(sc for sc in SubCategory if sc.category == Category[category_id])[:]
    if level:
        if parent_subcategory:
            return select(sc for sc in SubCategory if sc.category == Category[category_id] and sc.level == level and sc.parentSubCategory.id == parent_subcategory)[:]
        else:
            return select(sc for sc in SubCategory if sc.category == Category[category_id] and sc.level == level)[:]

@db_session()
def delete_subcategory(id : int = None, name : str = None, category_id : int = None):
    if id:
        SubCategory[id].delete()
    if name:
        SubCategory.get(name=name, category=Category[category_id]).delete()

@db_session()
def subcategory_exists(name : str, category : str):
    category=Category.get(name=category)
    if category:
        return SubCategory.exists(name=name, category=category)
    else:
        return False


# Promocode
@db_session()
def create_promocode(name : str):
    return Promocode(name=name)

@db_session()
def get_promocode(id : int = None, name : str = None, tg_id : str = None, users : bool = False, category_id : int = None, categories : bool = False):
    if id:
        if users:
            return select(u for u in Promocode[id].users)[:]
        if categories:
            return select(c for c in Promocode[id].categories.category)[:]
        else:
            return Promocode[id]
    if name:
        return Promocode.get(name=name)
    if tg_id and not category_id:
        return select(p for p in Promocode if User.get(tg_id=tg_id) in p.users)[:]
    if tg_id and category_id:
        return select(p for p in Promocode if User.get(tg_id=tg_id) in p.users and category_id in (pc.category.id for pc in p.categories))[:]
    else:
        return select(p for p in Promocode)[:]
    
@db_session()
def update_promocode(name : str, discount : int = None, categories : list = None, tg_id : str = None):
    promocode_to_update = Promocode.get(name=name)
    if discount and not categories:
        promocode_to_update.discount = discount
    if categories and not discount:
        categories_obj = [get_category(id=cat) for cat in categories]
        promocode_to_update.categories = categories_obj
    if categories and discount:
        categories_obj = [get_category(id=cat) for cat in categories]
        for cat in categories_obj:
            if promocodecategory_exists(promocode_id=promocode_to_update.id, category_id=cat.id):
                pass
            else:
                create_promocodecategory(promocode_id=promocode_to_update.id, category_id=cat.id, discount=discount)
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
def get_promoprice(product : Product, tg_id : int):
    user_promocodes = get_promocode(tg_id=tg_id)
    if len(user_promocodes) == 0:
        return product.price
    else:
        price = []
        for promocode in user_promocodes:
            if product.category.id in [promcat.category.id for promcat in promocode.categories]:
                promcat = get_promocodecategory(promocode_id=promocode.id, category_id=product.category.id)
                price.append(int(product.price * (1 - promcat.discount / 100)))
        if price:
            return min(price)
        else:
            return product.price
    

# PromocodeCategory
@db_session()
def create_promocodecategory(promocode_id : int, category_id : int, discount : int):
    return Promocode_Category(promocode=Promocode[promocode_id], category=Category[category_id], discount=discount)

@db_session()
def get_promocodecategory(promocode_id : int, category_id : int = None):
    if promocode_id and category_id:
        return Promocode_Category.get(promocode=Promocode[promocode_id], category=Category[category_id])
    else:
        return select(p for p in Promocode_Category if p.promocode == Promocode[promocode_id])[:]

@db_session()
def update_promocodecategory(promocode_id : int, category_id : int, discount : int):
    promcat_to_update = Promocode_Category.get(promocode=Promocode[promocode_id], category=Category[category_id])
    promcat_to_update.discount = discount
    return promcat_to_update

@db_session()
def delete_promocodecategory(promocode_id : int, category_id : int):
    promcat_to_delete = Promocode_Category.get(promocode=Promocode[promocode_id], category=Category[category_id])
    promcat_to_delete.delete()

@db_session()
def promocodecategory_exists(promocode_id : int, category_id : int):
    return Promocode_Category.exists(promocode=Promocode[promocode_id], category=Category[category_id])

#Order
@db_session()
def create_order(tg_id : str, products : list):
    order = Order(user=User.get(tg_id=tg_id))
    for product in products:
        Order_Product(order=order, product=product.article, sizes=product.sizes)
    return order

@db_session()
def get_order(id : int = None, tg_id : str = None, category_id : int = None):
    if id:
        return Order[id]
    if tg_id:
        return Order.get(user=User.get(tg_id=tg_id))

@db_session()
def update_order(id : int = None, tg_id : str = None, status : str = None, comment : str = None):
    if id:
        order_to_update = Order[id]
    if tg_id:
        order_to_update = Order.get(user=User.get(tg_id=tg_id))
    if status:
        order_to_update.status = status
    if comment:
        order_to_update.comment = comment
    return order_to_update

@db_session()
def delete_order(id : int = None):
    Order[id].delete()

#Log
@db_session()
def create_log(tg_id : str, action : str):
    log = Log(user=User.get(tg_id=tg_id), action=action)
    return log

@db_session()
def get_log(id : int = None, tg_id : str = None):
    if id:
        return Log[id]
    if tg_id:
        return select(l for l in Log if l.user == User.get(tg_id=tg_id))[:]
    else:
        return [list(i)[:-1] + [list(i)[-1].strftime('%d.%m.%Y %H:%M:%S')] for i in select([log.id, log.user.tg_id, log.user.username, log.user.first_name, log.user.last_name, log.action, log.datetime] for log in Log)[:]]
    