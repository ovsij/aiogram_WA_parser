from aiogram.types import Message
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pony.orm import *

db = Database()


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class Status(Enum):
    START = 'Создан'
    ORDERED = 'Заказан с сайта'
    RECIEVED = 'Получен на склад'
    DELIVERED = 'Отправлен клиенту'
    CLOSED = 'Отменен'
    CANCELED = 'Завершен'

class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    tg_id = Optional(str)
    username = Optional(str, unique=True)
    first_name = Optional(str, nullable=True)
    last_name = Optional(str, nullable=True)
    phone = Optional(str, nullable=True)
    address = Optional(str, nullable=True)
    sizes = Optional(str, nullable=True)
    shoe_sizes = Optional(str, nullable=True)
    brands = Optional(str, nullable=True)
    prices = Optional(str, nullable=True)
    carts = Set('Cart')
    promocode = Set('Promocode')
    categories = Set('Category')
    orderd = Set('Order')
    first_usage = Optional(datetime, default=lambda: datetime.now())
    last_usage = Optional(datetime, default=lambda: datetime.now())
    is_banned = Optional(bool, default=False)
    state = Optional(str, nullable=True)

class Cart(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    product = Required('Product')
    sizes = Required(str)

class Product(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    category = Required('Category')
    subcategory = Required('SubCategory')
    description = Optional(str, nullable=True)
    sizes = Optional(str, nullable=True)
    price = Optional(int)
    image = Optional(str, nullable=True)
    deleted = Optional(bool, default=False)
    edited = Optional(bool, default=False)
    article = Optional(str, nullable=True)
    url = Optional(str, nullable=True)
    carts = Set(Cart)

class SubCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    level = Required(int, default=1)
    parentSubCategory = Optional('SubCategory', nullable=True)
    childSubCategory = Set('SubCategory', nullable=True)
    category = Required('Category')
    product = Set(Product)

class Category(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    custom = Optional(bool, default=False)
    subcategory = Set(SubCategory)
    margin = Optional(int)
    phone = Optional(str, unique=True)
    metaCategory = Required('MetaCategory')
    promocodes = Set('Promocode_Category')
    product = Set(Product)
    users = Set(User)

class MetaCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    categories = Set(Category)

class Promocode(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    categories = Set('Promocode_Category')
    users = Set(User)

class Promocode_Category(db.Entity):
    id = PrimaryKey(int, auto=True)
    promocode = Required(Promocode)
    category = Required(Category)
    discount = Required(int)

class Order(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    products = Set('Order_Product')
    status = Required(str, default='Создан')
    datetime = Required(datetime, default=lambda: datetime.now())
    comment = Optional(str, nullable=True)
    

class Order_Product(db.Entity):
    id = PrimaryKey(int, auto=True)
    order = Required(Order)
    product = Required(str) # артикул товара
    sizes = Required(str)
    
