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
    carts = Set('Cart')
    promocods = Set('Promocode')
    first_usage = Optional(datetime, default=lambda: datetime.now())
    last_usage = Optional(datetime, default=lambda: datetime.now())
    is_banned = Optional(bool, default=False)

class Cart(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    product = Required(str)

class Product(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    category = Optional('Category')
    subcategory = Optional('SubCategory')
    catalog = Optional('Catalog')
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
    subcategory = Set(SubCategory)
    catalog = Required('Catalog')
    product = Set(Product)

class Catalog(db.Entity):
    id = PrimaryKey(int, auto=True)
    phone = Required(str, unique=True)
    link = Required(str)
    margin = Optional(int)
    promocodes = Set('Promocode')
    product = Set(Product)
    category = Set(Category)

class Promocode(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    discount = Required(int)
    catalogs = Set(Catalog)
    users = Set(User)
