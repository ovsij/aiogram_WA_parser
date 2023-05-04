from datetime import datetime
from decimal import Decimal
from enum import Enum
from pony.orm import *

db = Database()

class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

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
    promocode = Optional('Promocode')
    categories = Set('Category')
    first_usage = Optional(datetime, default=lambda: datetime.now())
    last_usage = Optional(datetime, default=lambda: datetime.now())
    is_banned = Optional(bool, default=False)

class Cart(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    product = Required(str)
    sizes = Required(str)

class Product(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    category = Optional('Category')
    subcategory = Optional('SubCategory')
    #catalog = Optional('Catalog')
    description = Optional(str, nullable=True)
    sizes = Optional(str, nullable=True)
    price = Optional(int)
    image = Optional(str, nullable=True)
    deleted = Optional(bool, default=False)
    edited = Optional(bool, default=False)
    article = Optional(str, nullable=True)

class SubCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    category = Required('Category')
    product = Set(Product)

class Category(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    custom = Optional(bool, default=False)
    subcategory = Set(SubCategory)
    margin = Optional(int)
    phone = Optional(str, unique=True)
    #catalog = Optional('Catalog', nullable=True)
    promocodes = Set('PromocodeCategory')
    product = Set(Product)
    users = Set(User)

class Promocode(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    categories = Set('PromocodeCategory')
    users = Set(User)

class PromocodeCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    promocode = Required(Promocode)
    category = Required(Category)
    discount = Required(int)