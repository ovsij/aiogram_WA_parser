from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.utils import exceptions
from dotenv import load_dotenv
import logging
import os
import re

load_dotenv()



from loader import dp, Form

from database.crud import *
from database.models import *
from keyboards.inline import *
from keyboards.reply import *
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
        text, reply_markup = inline_kb_subcategories(tg_id=str(callback_query.from_user.id), category=int(code[2]), page=int(code[-1]))
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
                sizes=code[4].strip('s='),
                prices=code[5].strip('p='),
                page=[int(p) for p in code[-2].split('-')],
                back=True,
                sort='n'
                )
            await callback_query.message.edit_text(
                text=textReply_markup[-1]['text'],
                reply_markup=textReply_markup[-1]['reply_markup']
            )
            return
            """
            if 's=' in code[4]:
                textReply_markup = inline_kb_listproducts(
                    tg_id=str(callback_query.from_user.id), 
                    category=int(code[2]), 
                    sub_category=int(code[3]),
                    sizes=code[4].strip('s='),
                    prices=code[5].strip('p='),
                    page=[int(p) for p in code[-1].split('-')]
                )
            """
        else:
            textReply_markup = inline_kb_listproducts(
                tg_id=str(callback_query.from_user.id), 
                category=int(code[2]), 
                sub_category=int(code[3]),
                sizes=code[4].strip('s=') if len(code[4].strip('s=')) > 0 else None,
                prices=code[5].strip('p=') if len(code[5].strip('p=')) > 0 else None,
                page=[int(p) for p in code[-1].split('-')],
                sort=code[6]
            )
        await callback_query.message.delete()
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
                    #reply_markup=item['reply_markup']
                )
                await bot.send_message(
                    callback_query.message.chat.id,
                    text = 'Выберите действие: ',
                    reply_markup=item['reply_markup']
                )

    if code[1] == 'sf':
        # если выбраны размеры выводится это
        #if 's=' in code[-1]:
        sizes = code[4].strip('s=').split('-') if code[4].strip('s=').split('-')[0] != '' else []
        prices = code[5].strip('p=').split('-') if code[5].strip('p=').split('-')[0] != '' else []
    
        text, reply_markup = inline_kb_sizefilter(category=code[2], sub_category=code[3], sizes_code_list=sizes, prices_code_list=prices, sort=code[6])
        # при превышении лимита в 6 размеров ничего не происходит
        if len(reply_markup['inline_keyboard'][-1][0]['callback_data'].split('_')[4].strip('s=').split('-')) > 6:
            return
        await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        # это первым или если не выбраны размеры
        #else:
        #    text, reply_markup = inline_kb_sizefilter(category=code[2], sub_category=code[3], page=[0,5])
        #    await callback_query.message.edit_text(
        #        text=text,
        #        reply_markup=reply_markup
        #        )

    if code[1] == 'pf':
        # если выбраны размеры выводится это
        #if 'p=' in code[-1]:
        sizes = code[4].strip('s=').split('-') if code[4].strip('s=').split('-')[0] != '' else []
        prices = code[5].strip('p=').split('-') if code[5].strip('p=').split('-')[0] != '' else []
        text, reply_markup = inline_kb_pricefilter(category=code[2], sub_category=code[3], sizes_code_list=sizes, prices=prices)
        if len(reply_markup['inline_keyboard'][-1][0]['callback_data'].split('_')[5].strip('p=').split('-')) > 3:
            return
        await callback_query.message.edit_text(
                text=text,
                reply_markup=reply_markup
            )
        ## это первым или если не выбраны цены
        #else:
        #    text, reply_markup = inline_kb_pricefilter(category=code[2], sub_category=code[3], sizes_code_list=code[4].strip('s=').split('-'), page=[0,5])
        #    await callback_query.message.edit_text(
        #        text=text,
        #        reply_markup=reply_markup
        #        )
        
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
            update_product(product_id=int(code[-1]), deleted=True)
        if code[1] == 'returnproduct':
            update_product(product_id=int(code[-1]), deleted=False)
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
        images = get_image(int(code[-1])).split('\n')
        
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
        if callback_query.message.caption.split(' ')[-1] == 'корзину!':
            return
        add_to_cart(tg_id=str(callback_query.from_user.id), prod_id=int(code[2]))
        text, reply_markup = inline_kb_product(tg_id=str(callback_query.from_user.id), id=int(code[2]))
        text += '\n\nТовар успешно добавлен в корзину!'
        await callback_query.message.edit_caption(
            caption=text,
            reply_markup=reply_markup
        )

    if code[1] == 'cart':
        text, reply_markup = await inline_kb_cart(callback_query.from_user)
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

    if code[1] == 'delete':
        del_from_cart(id=code[-1], tg_id=str(callback_query.from_user.id))
        text, reply_markup = await inline_kb_cart(callback_query.from_user)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

    if code[1] == 'deleteall':
        clean_cart(callback_query.from_user)
        text, reply_markup = await inline_kb_cart(callback_query.from_user)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )

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
    
    if code[1] == 'change':
        if code[-1] == 'phone':
            await Form.user_phone.set()
            text, reply_markup = reply_kb_change(param='phone')
            Form.prev_message = await bot.send_message(
                callback_query.from_user.id, 
			    text = text,
                reply_markup=reply_markup)
            
        if code[-1] == 'address':
            await Form.user_address.set()
            text = reply_kb_change(param='address')
            Form.prev_message = await bot.send_message(
                callback_query.from_user.id, 
			    text = text,
            )
    
    if code[1] == 'admin':
        text, reply_markup = inline_kb_admin()
        await callback_query.message.edit_text(
            text=text,
            reply_markup=reply_markup
        )
    
    if code[1] == 'sendmessage':
        text = 'Введите текст сообщения'
        await Form.new_message.set()
        Form.prev_message = await callback_query.message.edit_text(
            text=text
        )
    
    if code[1] == 'addcatalog':
        text = 'Пришлите номер аккаунта в котором находится каталог в формате: 393421807916'
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


            

# Рассылка сообщения
@dp.callback_query_handler(lambda c: c.data == 'aceptsending', state=Form.new_message)
async def acceptsending(callback_query: types.CallbackQuery, state: FSMContext):
    print(f'User {callback_query.from_user.id} open {callback_query.data}')

    
    async with state.proxy() as data:
        data['new_message'] = callback_query.message.text

    text = data['new_message']

    for user_id in get_users():
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
    
