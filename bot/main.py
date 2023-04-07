import asyncio
from os.path import getctime
import datetime

from aiogram import types
from aiogram.utils import executor
import logging

from loader import dp, bot


import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(
                  os.path.dirname(__file__), 
                  os.pardir)
)
sys.path.append(PROJECT_ROOT)

from database.crud import *
from parser import parser

logging.basicConfig(level=logging.INFO)


async def scheduled_catalogs(wait_for):
    while True:
        catalogs = get_catalogs()
        for catalog in catalogs:
            if catalog.phone not in ['valentino', 'lesilla']:
                url = f'https://web.whatsapp.com/catalog/{catalog.phone}'
                items = await parser.get_catalog(url=url)
                del_products(catalog=catalog.phone)
                for item in items:
                    price = int((item[4] * (euro_cost() + 1)) / 100 * get_catalog(phone=catalog.phone).margin) if item[4] else None
                    try:
                        description_cost = int((float(item[3].split(',00')[0].split(' ')[-1].replace('.', '') + '.00') * (euro_cost() + 1)) / 100 * get_catalog(phone=catalog.phone).margin)
                        description = item[3].replace(item[3].split(',00')[0].split(' ')[-1] + ',00', str(description_cost)).replace('€', 'руб.')
                    except:
                        description = None
                    create_product(name=item[0], category=item[1], subcategory=item[2], catalog=catalog.phone, description=description, price=price, image=item[5])
        await asyncio.sleep(wait_for)

async def scheduled_valentino(loop, wait_for):
    while True:
        #try:
        await parser.get_valentino(loop)
        #except Exception as ex:
        #    print(ex)
        
        await asyncio.sleep(wait_for)
            

async def send_mes(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        screen_time = datetime.fromtimestamp(getctime('parser/screenshot.png'))
        if datetime.now() - screen_time <= timedelta(minutes=1):
            #await bot.send_message(227184505, 'Отсканируй QR')
            photo = types.InputFile('parser/screenshot.png')
            await bot.send_photo(
                227184505, 
                photo=photo, 
                caption='Для входа в аккаунт WhatsApp отсканируйте QR-код. Он действителен 2 минуты.'
            )
            await asyncio.sleep(60)


if __name__ == '__main__':
    from handlers import dp
    loop = asyncio.get_event_loop()
    #loop.create_task(parser.get_valentino())
    #loop.create_task(scheduled_catalogs(86400))
    loop.create_task(send_mes(5))
    loop.create_task(scheduled_valentino(loop, 7200))
    executor.start_polling(dp, skip_updates=True)