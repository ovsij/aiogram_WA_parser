from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.utils import exceptions, markdown
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import os
import re

load_dotenv()

from loader import dp, Form

from database.crud import *
from database.db import *
from database.models import *
from keyboards.inline import *
from keyboards.reply import *
from keyboards.constructor import InlineConstructor
from parser import parser

import asyncio

# исключение при флуде от бота
@dp.errors_handler(exception=exceptions.RetryAfter)
async def exception_handler(update: types.Update, exception: exceptions.RetryAfter):
    # Do something
    return True

# обработчик кнопок
@dp.callback_query_handler(lambda c: c.data.startswith('btn'))
async def btn_callback(callback_query: types.CallbackQuery):
    if datetime.now() - get_user(tg_id=str(callback_query.from_user.id)).last_usage < timedelta(seconds=0.5):
        return
    update_user(tg_id=str(callback_query.from_user.id), last_usage=True)
    code = callback_query.data.split('_')
    logging.info(f'User {callback_query.from_user.id} open {code}')

    if code[1] == 'menu':
        text, reply_markup = inline_kb_menu(callback_query.from_user)
        if str(callback_query.from_user.id) in os.getenv("ADMINS"):
            reply_markup.add(btn_admin())
        try:
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        except:
            await callback_query.message.delete()
            await bot.send_message(
                callback_query.from_user.id,
                text=text,
                reply_markup=reply_markup
            )

    if code[1] == 'catalog':
        text, reply_markup = inline_kb_categories(tg_id=str(callback_query.from_user.id), page=int(code[-1]))
        try:
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        except:
            await callback_query.message.delete()
            await bot.send_message(
                callback_query.from_user.id,
                text=text,
                reply_markup=reply_markup
            )
    
    if code[1] == 'category':
        try:
            subcategory = int(code[3].split('-')[0])
            level = int(code[3].split('-')[1]) + 1
        except:
            subcategory = None
            level = 1
        
        text, reply_markup = inline_kb_subcategories(tg_id=str(callback_query.from_user.id), category=int(code[2]), subcategory=subcategory, level=level, page=int(code[-1]))
        try:
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        except:
            await callback_query.message.delete()
            await bot.send_message(
                callback_query.message.chat.id,
                text=text, 
                reply_markup=reply_markup
            )

    if code[1] == 'ls':
        # кнопка назад из меню выбора размеров
        if code[-1] == 'back':
            textReply_markup = inline_kb_listproducts(
                tg_id=str(callback_query.from_user.id), 
                category=int(code[2]), 
                sub_category=int(code[3]),
                sizes=code[4].replace('s=', ''),
                prices=code[5].replace('p=', ''),
                page=[int(p) for p in code[-2].split('-')],
                back=True,
                sort='n'
                )
            
            await callback_query.message.edit_text(
                text=textReply_markup[-1]['text'],
                reply_markup=textReply_markup[-1]['reply_markup']
            )
            return
          
        else:
            textReply_markup = inline_kb_listproducts(
                tg_id=str(callback_query.from_user.id), 
                category=int(code[2]), 
                sub_category=int(code[3]),
                sizes=code[4].replace('s=', '') if len(code[4].replace('s=', '')) > 0 else None,
                prices=code[5].replace('p=', '') if len(code[5].replace('p=', '')) > 0 else None,
                page=[int(p) for p in code[-1].split('-')],
                sort=code[6]
            )
        try:
            await callback_query.message.delete()
        except:
            pass
        # последнее сообщение с кнопками
        print(textReply_markup)
        for item in textReply_markup:
            if not item['images']:
                await bot.send_message(
                    callback_query.message.chat.id,
                    text=item['text'], 
                    reply_markup=item['reply_markup']
                )
            else:
                
                try:
                    # карточка товара с фото
                    images = item['images'].split('\n')
                    photo = [types.InputMedia(media=open(img, 'rb'), caption=item['text']) if images.index(img) == 0 else types.InputMedia(media=open(img, 'rb')) for img in images]
                    await bot.send_media_group(
                        callback_query.message.chat.id, 
                        media=photo,
                    )
                    # сообщение м кнопками под товаром "добавить в корзину" и тд
                    await bot.send_message(
                        callback_query.message.chat.id,
                        text = 'Выберите действие: ',
                        reply_markup=item['reply_markup']
                    )
                    #await asyncio.sleep(0.5)
                except:
                    continue
    if code[1] == 'publish':
        text, reply_markup, images = inline_kb_publish(product_id=code[-1], to=code[2])
        
        photo = [types.InputMedia(media=open(img, 'rb'), caption=text) if images.index(img) == 0 else types.InputMedia(media=open(img, 'rb')) for img in images]
        
        chat_id = -1001617464327 if code[2] == 'channel' else callback_query.from_user.id
        
        await bot.send_media_group(
            chat_id, 
            media=photo,
        )

        await bot.send_message(
            chat_id,
            text = 'Выберите действие: ',
            reply_markup=reply_markup
        )

    if code[1] == 'sf':
        # если выбраны размеры выводится это
        sizes = code[4].replace('s=', '').split('-') if code[4].strip('s=').split('-')[0] != '' else []
        prices = code[5].replace('p=', '').split('-') if code[5].strip('p=').split('-')[0] != '' else []
    
        text, reply_markup = inline_kb_sizefilter(category=code[2], sub_category=code[3], sizes_code_list=sizes, prices_code_list=prices, sort=code[6])
        # при превышении лимита в 6 размеров ничего не происходит
        if len(reply_markup['inline_keyboard'][-1][0]['callback_data'].split('_')[4].replace('s=', '').split('-')) > 6 or len(reply_markup['inline_keyboard'][-1][0]['callback_data'].split('_')[4].replace('s=', '')) > 30:
            return
        await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        

    if code[1] == 'pf':
        # если выбраны размеры выводится это
        sizes = code[4].replace('s=', '').split('-') if code[4].replace('s=', '').split('-')[0] != '' else []
        prices = code[5].replace('p=', '').split('-') if code[5].replace('p=', '').split('-')[0] != '' else []
        text, reply_markup = inline_kb_pricefilter(category=code[2], sub_category=code[3], sizes_code_list=sizes, prices=prices)
        if len(reply_markup['inline_keyboard'][-1][0]['callback_data'].split('_')[5].replace('p=', '').split('-')) > 3:
            return
        await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
       
        
    if code[1] == 'subcategory':
        message_to_delete = Form.prev_message
        text, reply_markup = inline_kb_products(tg_id=str(callback_query.from_user.id), category=int(code[2]), sub_category=int(code[3]), page=int(code[-1]))
        try:
            Form.prev_message = await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
            if type(message_to_delete) == list:
                for mes in message_to_delete:
                    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=mes.message_id)
        except:
            await callback_query.message.delete()
            await bot.send_message(
                callback_query.message.chat.id,
                text=text, 
                reply_markup=reply_markup
            )

    if 'product' in code[1]:
        if code[1] == 'delproduct':
            product = get_product(id=int(code[-1]))
            if get_category(id=product.category.id).custom:
                del_product(id=int(code[-1]), forever=True)
                text, reply_markup = inline_kb_products(tg_id=str(callback_query.from_user.id), category=product.category.id, sub_category=product.subcategory.id, page=1)
                try:
                    Form.prev_message = await callback_query.message.edit_text(
                        text=text,
                        reply_markup=reply_markup
                    )
                    if type(message_to_delete) == list:
                        for mes in message_to_delete:
                            await bot.delete_message(chat_id=callback_query.from_user.id, message_id=mes.message_id)
                    return
                except:
                    await callback_query.message.delete()
                    await bot.send_message(
                        callback_query.message.chat.id,
                        text=text, 
                        reply_markup=reply_markup
                    )
                    return
            else:
                update_product(product_id=int(code[-1]), deleted=True)
        if code[1] == 'returnproduct':
            update_product(product_id=int(code[-1]), deleted=False)
        if code[1] == 'addproduct':
            category = get_category(id=int(code[2]))
            subcategory = get_subcategory(id=int(code[3]))
            product = create_product(name='New product', category=category.name, subcategory=subcategory.name)
            update_product(product_id=product.id, article=str(product.id))
            await Form.edit_name.set()
            Form.prev_message = await callback_query.message.edit_text(text=f'Введите новое наименование товара №{product.id}:')
            return
        if code[1] == 'editproduct':
            if code[2] == 'name':
                await Form.edit_name.set()
                Form.prev_message = await callback_query.message.edit_text(text=f'Введите новое наименование товара №{code[-1]}:')
                return
            if code[2] == 'description':
                await Form.edit_description.set()
                Form.prev_message = await callback_query.message.edit_text(text=f'Введите новое описание товара №{code[-1]}:')
                return
            if code[2] == 'price':
                await Form.edit_price.set()
                Form.prev_message = await callback_query.message.edit_text(text=f'Введите новую цену товара №{code[-1]}:')
                return
            if code[2] == 'sizes':
                await Form.edit_sizes.set()
                Form.prev_message = await callback_query.message.edit_text(text=f'Введите размеры через запятую (например: 36, 37, 38, 39). Товар №{code[-1]}:')
                return
            if code[2] == 'images':
                product = get_product(id=int(code[3]))
                if product.image:
                    for image in product.image.split('\n'):
                        os.remove(image)
                update_product(product_id=int(code[3]), image=' ')
                await Form.edit_images.set()
                Form.prev_message = await callback_query.message.edit_text(text=f'Пришлите в одном сообщении одну или несколько фотографий товара №{code[-1]}:')
                return
            # выбрать что изменить (первый шаг)
            text, reply_markup = inline_kb_editproduct(product_id=code[-1])
            await callback_query.message.edit_text(
                text=text, 
                reply_markup=reply_markup)
            return
        if code[1] == 'uneditproduct':
            update_product(product_id=int(code[-1]), edited=False)
            text, reply_markup = inline_kb_editproduct(product_id=code[-1])
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
            return
        
        text, reply_markup = inline_kb_product(tg_id=str(callback_query.from_user.id), id=int(code[-1]))
        try:
            images = get_image(int(code[-1])).split('\n')
        except:
            images = []
        
        if len(images) == 1:
            try:
                media = types.InputMedia(media=open(images[0], 'rb'), caption=text)
                await callback_query.message.edit_media(media=media, reply_markup=reply_markup)
            except:
                
                photo = types.InputFile(images[0])
                await bot.send_photo(
                    callback_query.message.chat.id, 
                    photo=photo, 
                    caption=text, 
                    reply_markup=reply_markup
                )
                try:
                    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=Form.prev_message.message_id)
                except:
                    pass
                await callback_query.message.delete()
        else:
            try:
                if type(Form.prev_message) == list:
                    message_to_delete = Form.prev_message
                    photo = [types.InputMedia(media=open(img, 'rb')) for img in images]
                    Form.prev_message = await bot.send_media_group(
                        callback_query.message.chat.id, 
                        media=photo, 
                    )
                    await bot.send_message(
                        callback_query.message.chat.id,
                        text=text, 
                        reply_markup=reply_markup
                    )
                    for mes in message_to_delete:
                        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=mes.message_id)
                    await callback_query.message.delete()
                else:
                    
                    photo = [types.InputMedia(media=open(img, 'rb')) for img in images]
                    Form.prev_message = await bot.send_media_group(
                        callback_query.message.chat.id, 
                        media=photo, 
                    )
                    await bot.send_message(
                        callback_query.message.chat.id,
                        text=text, 
                        reply_markup=reply_markup
                    )
                    await callback_query.message.delete()
            except:
                await bot.send_message(
                        callback_query.message.chat.id,
                        text=text, 
                        reply_markup=reply_markup
                    )
                await callback_query.message.delete()

    if code[1] == 'count':
        if code[3] == 'plus':
            counter = int(code[-1]) + 1
        elif code[3] == 'minus' and int(code[-1]) > 1:
            counter = int(code[-1]) - 1
        else:
            return
        text, reply_markup = inline_kb_product(tg_id=str(callback_query.from_user.id), id=int(code[2]), counter=counter)
        await callback_query.message.edit_caption(caption=text, reply_markup=reply_markup)

    if code[1] == 'tocart':
        if 's=' in code[-1]:
            sizes = code[-1].split('-')
            if len(sizes) > 6:
                return
            add_to_cart(tg_id=str(callback_query.from_user.id), product_id=int(code[2]), sizes=code[-1].strip('s=').replace('-', ', '))
            
            text, reply_markup = inline_kb_tocart(product_id=int(code[2]), sizes=code[-1].strip('s=').split('-'))
            text += f"\n\nРазмер(ы) в корзине: {code[-1].strip('s=').replace('-', ', ')}"
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        else:
            text, reply_markup = inline_kb_tocart(product_id=int(code[2]))
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
            #reply_markup = callback_query.message['reply_markup']
            #reply_markup['inline_keyboard'][0][0]['text'] = 'Удалить из корзины'
            #reply_markup['inline_keyboard'][0][0]['callback_data'] = f'btn_delfromcart_{code[-1]}'

    if code[1] == 'delfromcart':
        delete_from_cart(tg_id=str(callback_query.from_user.id), product_id=code[-1])
        reply_markup = callback_query.message['reply_markup']
        reply_markup['inline_keyboard'][0][0]['text'] = 'Добавить в корзину'
        reply_markup['inline_keyboard'][0][0]['callback_data'] = f'btn_tocart_{code[-1]}'
        await callback_query.message.edit_text(
            text = callback_query.message['text'],
            reply_markup=reply_markup
        )

    
    if code[1] == 'cart':
        if code[-1] == 'cart':
            textReply_markup  = await inline_kb_cart(tg_id=str(callback_query.from_user.id), page=[0, 5])
            for item in textReply_markup:
                if not item['images']:
                    await callback_query.message.edit_text(
                        text=item['text'], 
                        reply_markup=item['reply_markup']
                    )
        else:
            textReply_markup  = await inline_kb_cart(tg_id=str(callback_query.from_user.id), page=[int(p) for p in code[-1].split('-')])
            for item in textReply_markup:
                if not item['images']:
                    await bot.send_message(
                        callback_query.message.chat.id,
                        text=item['text'], 
                        reply_markup=item['reply_markup']
                    )
                else:
                    images = item['images'].split('\n')
                    photo = [types.InputMedia(media=open(img, 'rb'), caption=item['text']) if images.index(img) == 0 else types.InputMedia(media=open(img, 'rb')) for img in images]
                    await bot.send_media_group(
                        callback_query.message.chat.id, 
                        media=photo,
                    )
                    await bot.send_message(
                        callback_query.message.chat.id,
                        text='Выберите действие',
                        reply_markup=item['reply_markup']
                    )

    if code[1] == 'createorder':
        if code[-1] == '1':
             # создание заказа
            cart = get_cart(tg_id=str(callback_query.from_user.id))
            order = create_order(tg_id=str(callback_query.from_user.id), products=cart)

            # отправка в чат
            user = get_user(tg_id=str(callback_query.from_user.id))
            promocodes = get_promocode(tg_id=str(callback_query.from_user.id))
            promocodes_text = '' if promocodes else 'Нет'
            if promocodes:
                for promocode in promocodes:
                    promocodes_text += f'{promocode.name}, '
                promocodes_text = promocodes_text.strip(', ')

            sum = 0
            i = 1
            order_text = 'Состав заказа:'
            for product in cart:
                price = get_promoprice(product=product[0], tg_id=str(callback_query.from_user.id))
                category = get_category(id=product[0].category.id)
                order_text += f'\n {i}. {category.name} | {markdown.link(product[0].name, product[0].url)} ({product[1]}) - {price} руб. | {product[0].article}'
                sum += price
                i += 1
            order_text += f'\n\nИтого: {sum} руб.'

            cart = get_cart(tg_id=str(callback_query.from_user.id))
            order_text = markdown.text(
                f'Заказ № {order.id}\n',
                'Статус: Создан\n',
                'Менеджер:',
                '~\n',
                f'Покупатель:',
                f'{user.first_name} {user.last_name}',
                f'@{user.username} | {user.phone}\n',
                f'Промокоды:',
                f'{promocodes_text}\n',
                f'{order_text}',
                '---------------',
                sep='\n'
            )
            reply_markup = InlineConstructor.create_kb([
                ['Взять в работу', f'btn_orderstatus_{order.id}_2'],
                ['Добавить комментарий', f'btn_ordercomment_{order.id}']], [1, 1])
            await bot.send_message(-1001810938907, text=order_text, reply_markup=reply_markup, parse_mode='Markdown')
            text, reply_markup = inline_kb_createorder(tg_id=str(callback_query.from_user.id), create=bool(int(code[-1])), order_id=order.id)
        else:
            text, reply_markup = inline_kb_createorder(tg_id=str(callback_query.from_user.id), create=bool(int(code[-1])))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'orderstatus':
        status = {
            '1' : 'Создан',
            '2' : 'Взят в работу',
            '3' : 'Заказан с сайта',
            '4' : 'Получен на склад',
            '5' : 'Отправлен клиенту',
            '6' : 'Завершен'
        }
        order = update_order(id=int(code[2]), status=status[code[3]])
        text = callback_query.message.text
        text = text.replace(text.split('Статус: ')[1].split('\n')[0], status[code[3]])
        if code[3] == '1':
            text = text.split('Менеджер:')[0] + 'Менеджер:\n' + '~' + text.split('Менеджер:')[1].split('~')[1]
            text_and_data = [
                [status[str(int(code[3]) + 1)], f'btn_orderstatus_{order.id}_{str(int(code[3]) + 1)}'],
                ['Добавить комментарий', f'btn_ordercomment_{order.id}']
            ]
            reply_markup = InlineConstructor.create_kb(text_and_data, [1, 1])
        elif code[3] == '2':
            text = text.split('Менеджер:')[0] + 'Менеджер:\n' + f'@{callback_query.from_user.username}~' + text.split('Менеджер:')[1].split('~')[1]
            
            text_and_data = [
                [status[str(int(code[3]) + 1)], f'btn_orderstatus_{order.id}_{str(int(code[3]) + 1)}'],
                ['Откатить статус', f'btn_orderstatus_{order.id}_{str(int(code[3]) - 1)}'],
                ['Добавить комментарий', f'btn_ordercomment_{order.id}']
            ]
            reply_markup = InlineConstructor.create_kb(text_and_data, [1, 1, 1])
        elif code[3] == '6':
            text_and_data = [
                ['Откатить статус', f'btn_orderstatus_{order.id}_{str(int(code[3]) - 1)}'],
                ['Добавить комментарий', f'btn_ordercomment_{order.id}']
            ]
            reply_markup = InlineConstructor.create_kb(text_and_data, [1, 1])
        else:
            text_and_data = [
                [status[str(int(code[3]) + 1)], f'btn_orderstatus_{order.id}_{str(int(code[3]) + 1)}'],
                ['Откатить статус', f'btn_orderstatus_{order.id}_{str(int(code[3]) - 1)}'],
                ['Добавить комментарий', f'btn_ordercomment_{order.id}']
            ]
            reply_markup = InlineConstructor.create_kb(text_and_data, [1, 1, 1])
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'ordercomment':
        Form.order_message = callback_query.message
        await Form.add_comment.set()
        order = get_order(id=int(code[2]))
        Form.prev_message = await bot.send_message(
            -1001810938907,
            text = f'Введите комментарий к заказу №{order.id}'
        )

    if code[1] == 'phone':
        await callback_query.message.delete()
        await Form.user_phone.set()
        text, reply_markup = reply_kb_phone()
        await bot.send_message(
            callback_query.from_user.id, 
            text = text,
            reply_markup=reply_markup)

    if code[1] == 'orders':
        if int(code[-1]) > 0:
            page = int(code[-1])
        else:
            page = 1
        text, reply_markup = inline_kb_orders(callback_query.from_user, page=page)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'order':
        text, reply_markup = inline_kb_order(callback_query.from_user, id=int(code[2]), page=int(code[-1]))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'terms':
        text, reply_markup = inline_kb_terms(callback_query.from_user)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'contact':
        text, reply_markup = inline_kb_contact()
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
    
    if code[1] == 'lk':
        text, reply_markup = inline_kb_lk(str(callback_query.from_user.id))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'mysizes':
        update_user(tg_id=str(callback_query.from_user.id), sizes=code[2])
        text, reply_markup = inline_kb_mysizes(sizes=code[2])
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
    
    if code[1] == 'mshs':
        if len(code[2].split('-')) > 10:
            return
        update_user(tg_id=str(callback_query.from_user.id), shoe_sizes=code[2])
        text, reply_markup = inline_kb_myshoesizes(sizes=code[2].split('-'))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
    
    if code[1] == 'mybr':
        update_user(tg_id=str(callback_query.from_user.id), brands=code[2])
        text, reply_markup = inline_kb_mybrands(brands=code[2].split('-'))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
    
    if code[1] == 'pr':
        update_user(tg_id=str(callback_query.from_user.id), prices=code[2])
        text, reply_markup = inline_kb_myprices(prices=code[2])
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'promocode':
        await Form.promocode_user.set()
        reply_markup = InlineConstructor.create_kb([['Отмена','deny']], [1])

        Form.prev_message = await bot.send_message(
            callback_query.message.chat.id,
            text='Для отмены этого действия нажмите на кнопку\n\nДля продолжения введите промокод:',
            reply_markup=reply_markup
        )

    if code[1] == 'sizes':
        text, reply_markup = inline_kb_sizes(category_id=code[-1])
        photo = types.InputFile('database/sizes.PNG')
        
        await bot.send_photo(
            callback_query.message.chat.id, 
            photo=photo, 
            caption=text, 
            reply_markup=reply_markup
        )

    if code[1] == 'hide':
        await callback_query.message.delete()

    if code[1] == 'howto':
        text, reply_markup = inline_kb_howto()
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
        
    if code[1] == 'admin':
        text, reply_markup = inline_kb_admin()
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
    
    if code[1] == 'wacatalogs':
        text, reply_markup = inline_kb_wacatalogs()
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'promocodes':
        text, reply_markup = inline_kb_promocodes()
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
        
    if code[1] == 'editpromocode':
        text, reply_markup = inline_kb_editpromocode(promocode_id=int(code[2]))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'userspromocode':
        name = get_promocode(id=int(code[2])).name
        users = [f'Список пользователей, активировавших промокод {name}: \n\n']
        
        for user in get_promocode(id=int(code[2]), users=True):
            user_str = f'- '
            if user.username:
                user_str += f'@{user.username} | '
            else:
                user_str += f'{user.tg_id} | '
            if user.first_name:
                user_str += f'{user.first_name} '
            if user.last_name:
                user_str += f'{user.last_name}'
            user_str += '\n'
            users.append(user_str)
        with open(f'{name} users.txt', 'w') as file:
            for line in users:
                file.write(line)
        await bot.send_document(callback_query.from_user.id, open(f'{name} users.txt', 'r'))
        os.remove(f'{name} users.txt')
    
    if code[1] == 'removepromocode':
        name = get_promocode(id=int(code[2])).name
        delete_promocode(id=int(code[2]))
        text, reply_markup = inline_kb_promocodes()
        text += f'\n\nПромокод {name} удален'

        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'addpromocode':
        await Form.addpromocode.set()
        Form.prev_message = await callback_query.message.edit_text(
            text='Пришлите название промокода:',
        )

    if code[1] == 'promocodecategory':
        update_promocode(name=get_promocode(id=code[2]).name, categories=[int(cat) for cat in code[3].split('-')], discount=int(code[4]))
        text, reply_markup = inline_kb_addpromocode_catalogs(name=get_promocode(id=code[2]).name, cat_ids=code[3].split('-'), discount=int(code[4]))
        await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        
    if code[1] == 'editpd':
        if len(code) == 3:
            text, reply_markup = inline_kb_editpromocodediscount(promocode_id=int(code[2]))
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        elif len(code) == 4:
            await Form.editpromocode_discount.set()
            Form.prev_message = await callback_query.message.edit_text(
                text=f'Введите новую скидку по промокоду "{get_promocode(id=int(code[2])).name}" для категории "{get_category(id=int(code[3])).name}"',
            )
        
    if code[1] == 'sendmessage':
        text = 'Введите текст сообщения'
        await Form.new_message.set()
        Form.prev_message = await callback_query.message.edit_text(
            text=text
        )
    
    if code[1] == 'addcatalog':
        text = 'Пришлите номер аккаунта в котором находится каталог в формате: 393421807916 \n Для отвены введите команду /stop'
        await Form.add_catalog.set()
        Form.prev_message = await callback_query.message.edit_text(
            text=text
        )

    if code[1] == 'delcatalog':
        if code[-1] == 'delcatalog':
            text, reply_markup = inline_kb_delcatalog()
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        else:
            delete_catalog(phone=code[2])
            text, reply_markup = inline_kb_delcatalog()
            text += f'\n\n Каталог {code[2]} удален'
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
    
    if code[1] == 'editcatalog':
        if code[-1] == 'editcatalog':
            text, reply_markup = inline_kb_editcatalog()
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        else:
            text = 'Пришлите какой процент наценки будет у этого каталога (двузначное число). Например: 20'
            await Form.add_margin.set()
            Form.cat_phone = code[-1]
            
            Form.prev_message =  await callback_query.message.edit_text(
                text=text
            )

    if code[1] == 'finditem':
        text = 'Пришлите артикул товара'
        await Form.find_item.set()
        Form.prev_message =  await callback_query.message.edit_text(
            text=text
        )

    if code[1] == 'updatecatalog':
        if code[-1] == 'accept':
            mesg = await callback_query.message.edit_text(
                text=f'Запущено обновление каталога {code[2]}. \nЭто может занять продолжительное время, пожалуйста, подождите.',
            )
            #
            
            url = f'https://web.whatsapp.com/catalog/{code[2]}'
            
            
            items = await parser.get_catalog(url=url)
            
            if items == 0:
                text, reply_markup = inline_kb_updatecatalog()
                text += f'\n\nОбновление каталога {code[2]} прервано. Отсканируйте QR-код и попробуйте еще раз.'
                await callback_query.message.edit_text(
                    text=text,
                    reply_markup=reply_markup
                )
            elif items == 1:
                text, reply_markup = inline_kb_updatecatalog()
                text += f'\n\nОбновление каталога {code[2]} прервано. Произошла неизвестная ошибка'
                await callback_query.message.edit_text(
                    text=text,
                    reply_markup=reply_markup
                )
            else:
                del_products(catalog=code[2])
                for item in items:
                    price = int((item[4] * (euro_cost() + 1)) / 100 * get_catalog(phone=code[2]).margin) if item[4] else None
                    try:
                        description_cost = int((float(item[3].split(',00')[0].split(' ')[-1].replace('.', '') + '.00') * (euro_cost() + 1)) / 100 * get_catalog(phone=code[2]).margin)
                        description = item[3].replace(item[3].split(',00')[0].split(' ')[-1] + ',00', str(description_cost)).replace('€', 'руб.')
                    except:
                        description = None
                    create_product(name=item[0], category=item[1], subcategory=item[2], catalog=code[2], description=description, price=price, image=item[5])
                await bot.delete_message(chat_id=callback_query.from_user.id, message_id=mesg.message_id)
                text, reply_markup = inline_kb_updatecatalog()
                text += f'\n\nОбновление каталога {code[2]} завершено'
                await bot.send_message(
                    callback_query.from_user.id,
                    text=text,
                    reply_markup=reply_markup
                )
        elif code[-1] == 'deny':
            text, reply_markup = inline_kb_updatecatalog()
            text += f'\n\nОбновление каталога {code[2]} отменено'
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        elif code[-1] == 'updatecatalog':
            text, reply_markup = inline_kb_updatecatalog()
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        else:
            text, reply_markup = inline_kb_approveupdatecapalog(phone=code[2])
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
    if code[1] == 'updateVALENTINO':
        if code[-1] == 'updateVALENTINO':
            text, reply_markup = inline_kb_approveupdatecapalog(custom='VALENTINO')
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        elif code[-1] == 'accept':

            mesg = await callback_query.message.edit_text(
                text=f'Запущено обновление каталога VALENTINO. \nЭто может занять продолжительное время, пожалуйста, подождите.',
            )
            items = await parser.get_valentino()
            del_products(category='VALENTINO')
            for item in items:
                price = int((item[5] * (euro_cost() + 1)) / 100 * get_catalog(phone='valentino').margin) if item[5] else None
                create_product(name=item[0], category=item[1], subcategory=item[2], catalog='valentino', description=item[4], price=price, image=item[6])
            
            await bot.delete_message(chat_id=callback_query.from_user.id, message_id=mesg.message_id)
            text, reply_markup = inline_kb_updatecatalog()
            text += f'\n\nОбновление каталога VALENTINO завершено'
            await bot.send_message(
                callback_query.from_user.id,
                text=text,
                reply_markup=reply_markup
            )
        elif code[-1] == 'deny':
            text, reply_markup = inline_kb_updatecatalog()
            text += f'\n\nОбновление каталога VALENTINO отменено'
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
    if code[1] == 'updateLESILLA':
        if code[-1] == 'updateLESILLA':
            text, reply_markup = inline_kb_approveupdatecapalog(custom='LESILLA')
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        elif code[-1] == 'accept':
            
            mesg = await callback_query.message.edit_text(
                text=f'Запущено обновление каталога LESILLA. \nЭто может занять продолжительное время, пожалуйста, подождите.',
            )
            #loop = asyncio.get_event_loop()
            #items = loop.run_until_complete(await parser.get_lesilla())

            items = await parser.get_lesilla()

            
            del_products(category='LeSILLA')
            for item in items:
                price = int((item[4] * (euro_cost() + 1)) / 100 * get_catalog(phone='lesilla').margin) if item[4] else None
                description = item[3].replace('€ ', ' ')
                for i in re.findall(r'\d*[.]\d\d', item[3]):
                    if i:
                        price_rub = str(int((float(i) * (euro_cost() + 1)) / 100 * get_catalog(phone='lesilla').margin))
                        description = description.replace(i, '<s>' + price_rub + ' руб.</s>  ')
                description = description.replace(f'<s>{price_rub} руб.</s>', f'{price_rub} руб.')
                create_product(name=item[0], category=item[1], subcategory=item[2], catalog=code[2], description=description, price=price, image=item[5])
            
            await bot.delete_message(chat_id=callback_query.from_user.id, message_id=mesg.message_id)
            text, reply_markup = inline_kb_updatecatalog()
            text += f'\n\nОбновление каталога LESILLA завершено'
            await bot.send_message(
                callback_query.from_user.id,
                text=text,
                reply_markup=reply_markup
            )
        elif code[-1] == 'deny':
            text, reply_markup = inline_kb_updatecatalog()
            text += f'\n\nОбновление каталога LESILLA отменено'
            await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )

    if code[1] == 'addcategory':
        await Form.add_category.set()
        Form.prev_message = await bot.send_message(
            callback_query.from_user.id, 
            'Для отмены введите /stop\n\nДля продолжения введите название новой категории:'
        )
    
    if code[1] == 'deletecategory':
        delete_category(id=code[2])
        text, reply_markup = inline_kb_categories(tg_id=str(callback_query.from_user.id))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'addsubcategory':
        await Form.add_subcategory.set()
        category = get_category(id=code[2])
        Form.prev_message = await bot.send_message(
            callback_query.from_user.id, 
            f'Для отмены введите /stop\n\nДля продолжения введите название новой подкатегории в категории "{category.name}"'
        )
    
    if code[1] == 'deletesubcategory':
        delete_category(id=code[2])
        text, reply_markup = inline_kb_categories(tg_id=str(callback_query.from_user.id))
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

# Рассылка сообщения
@dp.callback_query_handler(lambda c: c.data == 'aceptsending', state=Form.new_message)
async def acceptsending(callback_query: types.CallbackQuery, state: FSMContext):
    print(f'User {callback_query.from_user.id} open {callback_query.data}')

    
    async with state.proxy() as data:
        data['new_message'] = callback_query.message.text

    text = data['new_message']

    for user_id in [u.tg_id for u in get_users()]:
        try:
            await bot.send_message(
                user_id,
                text=text
            )
        except Exception as ex:
            print(ex)
    
    await state.finish()
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=Form.prev_message.message_id)

    text, reply_markup = inline_kb_admin()
    await bot.send_message(
        callback_query.from_user.id,
        text=text + '\n\n Сообщение отправлено пользователям.',
        reply_markup=reply_markup
    )

# Отмена рассылки сообщения
@dp.callback_query_handler(lambda c: c.data == 'denysending', state=Form.new_message)
async def denysending(callback_query: types.CallbackQuery, state: FSMContext):
    print(f'User {callback_query.from_user.id} open {callback_query.data}')

    await state.finish()
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=Form.prev_message.message_id)
    text, reply_markup = inline_kb_admin()
    await bot.send_message(
            callback_query.from_user.id,
            text=text + '\n\n Сообщение не разослано.', 
            reply_markup=reply_markup
            )

# Отмена 
@dp.callback_query_handler(lambda c: c.data == 'deny', state=Form.promocode_user)
async def denysending(callback_query: types.CallbackQuery, state: FSMContext):
    print(f'User {callback_query.from_user.id} open {callback_query.data}')

    await state.finish()
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=Form.prev_message.message_id)
    
    
