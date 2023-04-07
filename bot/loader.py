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
    user_address = State()
    menu_message = State()
    prev_message = State()
    new_message = State()
    add_catalog = State()
    add_margin = State()
    cat_phone = State()
