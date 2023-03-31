from aiogram import types
from bot.keyboards.buttons import *
from dotenv import load_dotenv
import os

load_dotenv()

from loader import bot, dp, Form
from bot.keyboards.inline import inline_kb_menu

from database.crud import *
from database.models import *

@dp.message_handler(commands=['start'])
async def bot_start(message: types.Message):
    register_user(message.from_user)
    text, reply_markup = inline_kb_menu(message.from_user)
    #create_demo_orders(str(message.from_user.id))
    if message.from_user.id in [227184505]:
        reply_markup.add(btn_admin())
    Form.menu_msg = await bot.send_message(
        message.from_user.id,
        text=text,
        reply_markup=reply_markup
    )