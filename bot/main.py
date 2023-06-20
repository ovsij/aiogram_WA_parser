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
from parser import comparator
from parser import parser

logging.basicConfig(level=logging.INFO)

async def scheduled_catalogs(wait_for):
    while True:
        try:
            """
            try:
                await bot.send_message(227184505, f'NIKE начал парсинг')
                await parser.get_nike()
                await asyncio.sleep(10)
            except:
                await bot.send_message(227184505, f'Nike - произошла ошибка')
            try:
                await bot.send_message(227184505, f'VALENTINO начал парсинг')
                await parser.get_valentino()
                await asyncio.sleep(10)
            except:
                await bot.send_message(227184505, f'VALENTINO - произошла ошибка')
            try:
                await bot.send_message(227184505, f'LeSILLA начал парсинг')
                await parser.get_lesilla()
                await asyncio.sleep(10)
            except:
                await bot.send_message(227184505, f'LeSILLA - произошла ошибка')
            """
            catalogs = get_catalogs()

            for catalog in catalogs:
                # тест
                if catalog.phone not in ['valentino', 'lesilla', 'nike']:# and catalog.phone == '390143686270':
                    try:
                        await bot.send_message(227184505, f'{catalog.phone} начал парсинг')
                        url = f'https://web.whatsapp.com/catalog/{catalog.phone}'
                        items = await parser.get_catalog(url=url)
                        del_products(catalog=catalog.phone)
                        not_deleted_items = [p.name for p in get_product(catalog=catalog.phone)]
                        #print([p.image for p in get_product(catalog=catalog.phone)])
                        #print(not_deleted_items)
                        hashes = [comparator.CalcImageHash(product.image.split('\n')[0]) for product in get_product(catalog=catalog.phone)]
                        #print(hashes)
                        for item in items:
                            diff = []
                            if item[0] in not_deleted_items:
                                print(item[5])
                                for hash in hashes:
                                    d = comparator.CompareHash(hash, comparator.CalcImageHash(item[5].split('\n')[0]))
                                    #print('diff: ')
                                    #print(d)
                                    diff.append(d)
                            #print(diff)
                            if len(diff) >= 1:
                                if min(diff) <= 1:
                                    print(f'dont add: {item[0]}')
                                    continue                                
                            
                            price = int((item[4] * (euro_cost() + 1)) / 100 * get_catalog(phone=catalog.phone).margin) if item[4] else None
                            try:
                                description_cost = int((float(item[3].split(',00')[0].split(' ')[-1].replace('.', '') + '.00') * (euro_cost() + 1)) * float(f'1.{get_catalog(phone=catalog.phone).margin}'))
                                description = item[3].replace(item[3].split(',00')[0].split(' ')[-1] + ',00', str(description_cost)).replace('€', 'руб.')
                            except:
                                description = None
                            if catalog.phone == '390143686270':
                                description = item[3]
                            prod = create_product(name=item[0], category=item[1], subcategory=item[2], catalog=catalog.phone, description=description, price=price, image=item[5])
                            print(f'add : {prod}')
                    except:
                        await bot.send_message(227184505, f'{catalog.phone} - произошла ошибка')
                        continue
            await asyncio.sleep(wait_for)
            
        except Exception as ex:
            print(ex)
            
            await asyncio.sleep(wait_for)

            

async def send_mes(wait_for):
    while True:
        try:
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
        except:
            continue

async def p():
    await parser.get_nike()



if __name__ == '__main__':
    from handlers import dp
    loop = asyncio.get_event_loop()
    #loop.create_task(get_hellyhansen())
    #loop.create_task(scheduled_catalogs(0))
    #loop.create_task(send_mes(5))
    #loop.create_task(scheduled_valentino(7200))
    #asyncio.run(send_mes(5))
    executor.start_polling(dp, skip_updates=True)
    #asyncio.run(scheduled_catalogs(0))