from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from dotenv import load_dotenv
import os

load_dotenv()


bot = Bot(token=os.getenv("TOKEN"), parse_mode='HTML') 
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    user_phone = State()
    menu_message = State()
    prev_message = State()
    new_message = State()
    add_catalog = State()
    add_margin = State()
    cat_phone = State()
    edit_name = State()
    edit_description = State()
    edit_price = State()
    edit_sizes = State()
    edit_images = State()
    find_item = State()
    promocode_user = State()
    addpromocode = State()
    addpromocode_discount = State()
    editpromocode_discount = State()
    add_category = State()
    add_subcategory = State()
    add_comment = State()
    order_message = State()
