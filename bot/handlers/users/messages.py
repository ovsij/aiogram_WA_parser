from aiogram import types
from aiogram.dispatcher import FSMContext
import os
import re
import time

from loader import bot, dp, Form

from database.crud import *
from database.db import *
from database.models import *
from keyboards.inline import *
from keyboards.reply import *
from keyboards.constructor import InlineConstructor


@dp.message_handler()
async def user_message(message: types.Message):
    if message.chat.id != -1001810938907:
        await message.delete()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.user_phone)
async def change_phone(message: types.Message, state: FSMContext):
    # записываем номер телефона
    update_user(tg_id=str(message.from_user.id), phone=message.contact.phone_number)
    await state.finish()
    # удаляем ненужные сообщения
    time.sleep(1)
    await message.delete()
    types.ReplyKeyboardRemove()
    # обновляем текст сообщения с заказом
    text, reply_markup = inline_kb_createorder(tg_id=str(message.from_user.id), create=False)
    await bot.send_message(
        message.from_user.id,
        text=text,
        reply_markup=reply_markup
    )

@dp.message_handler(state=Form.user_phone)
async def user_message(message: types.Message):
    await message.delete()
    
    _, reply_markup = reply_kb_phone()
    Form.prev_message = await bot.send_message(
                message.from_user.id, 
			    text='К сожалению, ввести номер телефона текстом не получится. Нажмите на кнопку "Поделиться номером телефона. \nЕсли вы не видите кнопку, нажмите за значек слева от микрофона внизу экрана, тогда кнопка появится',
                reply_markup=reply_markup
            )

# получаем текст сообщения для рассылки
@dp.message_handler(state=Form.new_message)
async def sendmessate_text(message: types.Message, state: FSMContext):
    text = message.text
    #Form.new_message = message.text
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()
    reply_markup = inline_sendmessage()
    Form.prev_message = await bot.send_message(
            message.from_user.id,
            text=text,
            reply_markup=reply_markup,
            )

# неверный формат номера каталога
@dp.message_handler(lambda message: len(message.text) != 12, state=Form.add_catalog)
async def add_catalog_wrong(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()
    text = 'Пришлите номер аккаунта в котором находится каталог в формате: 393421807916\n\n Номер телефона должен состоять из 12 цифр без пробелов и иных знаков'
    Form.prev_message = await bot.send_message(
            message.from_user.id,
            text=text,
            )

# получаем номер телефона для добавления каталога
@dp.message_handler(state=Form.add_catalog)
async def add_catalog_phone(message: types.Message, state: FSMContext):

    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    #text, reply_markup = inline_kb_admin()
    
    if not catalog_exists(phone=message.text):
        phone = message.text
        link = 'https://web.whatsapp.com/catalog/' + message.text
        create_catalog(phone=phone, link=link, margin=30)
        text = 'Пришлите какой процент наценки будет у этого каталога (двузначное число). Например: 20'
        await Form.add_margin.set()
        Form.cat_phone = message.text
        
    else:
        text = f'\n\nКаталог {message.text} уже существует'
    
    Form.prev_message = await bot.send_message(
                message.from_user.id,
                text=text,
                )
    
# неверный формат процента наценки
@dp.message_handler(lambda message: len(message.text) != 2, state=Form.add_margin)
async def add_catalog_margin_wrong(message: types.Message, state: FSMContext):
    await message.delete()

# получаем процент наценки каталога
@dp.message_handler(state=Form.add_margin)
async def add_catalog_margin(message: types.Message, state: FSMContext):

    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    #phone = get_catalog(id=max([c.id for c in get_catalogs()])).phone
    phone = Form.cat_phone
    update_catalog(phone=phone, margin=int(message.text))

    text, reply_markup = inline_kb_admin()
    text += f'\n\nВнесение изменений произошло успешно'
    await bot.send_message(
                message.from_user.id,
                text=text,
                reply_markup=reply_markup
                )

# получаем новое наименование товара
@dp.message_handler(state=Form.edit_name)
async def add_new_item_name(message: types.Message, state: FSMContext):
    product_id = Form.prev_message.text.split('№')[1].strip(':')
    product = get_product(id=product_id)
    if get_category(id=product.category.id).custom:
        update_product(product_id=int(product_id), name=message.text)
    else:
        update_product(product_id=int(product_id), name=message.text, edited=True)

    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    text, reply_markup = inline_kb_editproduct(product_id=int(product_id))
    text += f'\n\nВнесение изменений произошло успешно'
    await bot.send_message(
                message.from_user.id,
                text=text,
                reply_markup=reply_markup
                )

# получаем новое описание товара
@dp.message_handler(state=Form.edit_description)
async def add_new_item_description(message: types.Message, state: FSMContext):
    product_id = Form.prev_message.text.split('№')[1].strip(':')
    product = get_product(id=product_id)
    if get_category(id=product.category.id).custom:
        update_product(product_id=int(product_id), description=message.text)
    else:
        update_product(product_id=int(product_id), description=message.text, edited=True)

    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    text, reply_markup = inline_kb_editproduct(product_id=int(product_id))
    text += f'\n\nВнесение изменений произошло успешно'
    await bot.send_message(
                message.from_user.id,
                text=text,
                reply_markup=reply_markup
                )

# неверный формат цены
@dp.message_handler(lambda message: not re.fullmatch('\d*', message.text), state=Form.edit_price)
async def add_new_item_price_wrong(message: types.Message, state: FSMContext):
    await message.delete()
    await Form.prev_message.edit_text(text='Введите только целове число. Без точек, запятых, пробелов и указания валюты.')

# получаем новую цену товара
@dp.message_handler(state=Form.edit_price)
async def add_new_item_price(message: types.Message, state: FSMContext):
    product_id = Form.prev_message.text.split('№')[1].strip(':')
    product = get_product(id=product_id)
    if get_category(id=product.category.id).custom:
        update_product(product_id=int(product_id), price=int(message.text))
    else:
        update_product(product_id=int(product_id), price=int(message.text), edited=True)

    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    text, reply_markup = inline_kb_editproduct(product_id=int(product_id))
    text += f'\n\nВнесение изменений произошло успешно'
    await bot.send_message(
                message.from_user.id,
                text=text,
                reply_markup=reply_markup
                )

# получаем новые размеры товара
@dp.message_handler(state=Form.edit_sizes)
async def add_new_item_description(message: types.Message, state: FSMContext):
    product_id = Form.prev_message.text.split('№')[1].strip(':')
   
    product = get_product(id=int(product_id))
    try: # если описание None - произойдет исключение
        description = product.description.split('Sizes:')[0].strip('\n\n') + f'\n\nSizes: {message.text}'
    except:
        description = f'Sizes: {message.text}'
    if get_category(id=product.category.id).custom:
        update_product(product_id=int(product_id), description=description, sizes=message.text)
    else:
        update_product(product_id=int(product_id), description=description, sizes=message.text, edited=True)
    
    text, reply_markup = inline_kb_editproduct(product_id=int(product_id))
    text += f'\n\nВнесение изменений произошло успешно'
    
    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    await bot.send_message(
                message.from_user.id,
                text=text,
                reply_markup=reply_markup
                )

# получаем новые фото товара
@dp.message_handler(content_types=['photo'], state=Form.edit_images)
async def get_photo(message: types.Message, state: FSMContext):
    
    product = get_product(id=int(Form.prev_message.text.split('№')[-1].strip(':')))
    category = get_category(id=product.category.id)
    subcategory = get_subcategory(id=product.subcategory.id)
    if not os.path.exists(f"database/images/{category.name}"):
        os.mkdir(f"database/images/{category.name}")

    if not os.path.exists(f"database/images/{category.name}/{subcategory.name}"):
        os.mkdir(f"database/images/{category.name}/{subcategory.name}")
    
    
    img_path = ''
    for i, photo in enumerate(message.photo):
        if i == 3:
            await photo.download(destination_file=f'database/images/{category.name}/{subcategory.name}/{photo["file_unique_id"]}.png')
            img_path += f'database/images/{category.name}/{subcategory.name}/{photo["file_unique_id"]}.png'
            update_product(product_id=product.id, image=img_path + '\n', several_images=True)

    await state.finish()

# получаем артикул товара
@dp.message_handler(state=Form.find_item)
async def get_article(message: types.Message, state: FSMContext):
    await state.finish()
    article = message.text
    product = get_product(article=article)

    description = '' if not product.description else product.description
    price = 'Не указана' if not product.price else f'{product.price} руб.'
    text = f'{product.name}\n\nАртикул: {product.article}\n{description}\n\nЦена: {price}'
    text_and_data = [btn_back('admin')]
    schema = [1]
    reply_markup = InlineConstructor.create_kb(text_and_data, schema)

    images = product.image.split('\n')
        
    if len(images) == 1:
        photo = types.InputFile(images[0])
        await bot.send_photo(
            message.from_user.id, 
            photo=photo, 
            caption=text, 
            reply_markup=reply_markup
        )
    else:
        photo = [types.InputMedia(media=open(img, 'rb')) for img in images]
        await bot.send_media_group(
            message.from_user.id, 
            media=photo, 
        )
        await bot.send_message(
            message.from_user.id,
            text=text, 
            reply_markup=reply_markup
        )
# получаем название промокода от админа
@dp.message_handler(state=Form.addpromocode)
async def add_admin_promocode(message: types.Message, state: FSMContext):
    create_promocode(name=message.text.split(': ')[-1])

    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    await Form.addpromocode_discount.set()
    Form.prev_message = await bot.send_message(
        message.from_user.id,
        text=f'Введите общий размер скидки по промокоду: {message.text}\n(изменить размер скидки для конкретной категории можно будет позже)', 
    )

# получаем размер скидки от админа
@dp.message_handler(state=Form.addpromocode_discount)
async def add_admin_promocode_discount(message: types.Message, state: FSMContext):
    
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()
    try:
        i = int(message.text)
        if i < 1 or i > 99:
            Form.prev_message = await bot.send_message(
            message.from_user.id,
            text=f'Введите общий размер скидки по промокоду: {message.text}\n(введите целое число от 1 до 99)',
            )
            return
    except:
        Form.prev_message = await bot.send_message(
            message.from_user.id,
            text=f'Введите общий размер скидки по промокоду: {message.text}\n(введите целое число от 1 до 99)',
        )
        return
    await state.finish()

    text, reply_markup = inline_kb_addpromocode_catalogs(name=Form.prev_message.text.split(': ')[-1].split('\n')[0], discount=int(message.text))

    Form.prev_message = await bot.send_message(
            message.from_user.id,
            text=text,
            reply_markup=reply_markup
        )

# получаем новую скидку для категории
@dp.message_handler(state=Form.editpromocode_discount)
async def add_user_promocode(message: types.Message, state: FSMContext):
    
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()
    try:
        category = get_category(name=Form.prev_message.text.split('"')[-2])
        promocode = get_promocode(name=Form.prev_message.text.split('"')[-4])
        i = int(message.text)
        if i < 1 or i > 99:
            Form.prev_message = await bot.send_message(
            message.from_user.id,
            text=f'Введите новую скидку по промокоду "{promocode.name}" для категории "{category.name}"(введите целое число от 1 до 99)',
            )
            return
    except:
        Form.prev_message = await bot.send_message(
            message.from_user.id,
            text=f'Введите целое число от 1 до 99',
        )
        return
    await state.finish()
    update_promocodecategory(promocode_id=promocode.id, category_id=category.id, discount=int(message.text))
    text, reply_markup = inline_kb_editpromocode(promocode_id=promocode.id)
    await bot.send_message(
        message.from_user.id,
        text=text,
        reply_markup=reply_markup
    )
    
# получаем промокод от юзера
@dp.message_handler(state=Form.promocode_user)
async def add_user_promocode(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    if promocode_exists(name=message.text):
        promocode = get_promocode(name=message.text)
        if get_user(tg_id=str(message.from_user.id)).id in [u.id for u in get_promocode(id=promocode.id, users=True)]:
            pass
        else:
            update_user(tg_id=str(message.from_user.id), promocode=message.text)
        
        text, reply_markup = inline_kb_lk(tg_id=str(message.from_user.id))
        await bot.send_message(
            message.from_user.id, 
            text=text,
            reply_markup=reply_markup
        )
    else:
        await bot.send_message(message.from_user.id, f'Промокод {message.text} не существует')


# получаем название новой категории
@dp.message_handler(state=Form.add_category)
async def add_category(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()
    if not category_exists(name=message.text):
        create_category(name=message.text, margin=30, custom=True)
    text, reply_markup = inline_kb_categories(str(message.from_user.id))
    await bot.send_message(message.from_user.id, text=text, reply_markup=reply_markup)

# получаем название новой подкатегории
@dp.message_handler(state=Form.add_subcategory)
async def add_subcategory(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()
    if not subcategory_exists(name=message.text, category=Form.prev_message.text.split('"')[-2]):
        s = create_subcategory(name=message.text, category=Form.prev_message.text.split('"')[-2])
        print(s)
    category = get_category(name=Form.prev_message.text.split('"')[-2])
    text, reply_markup = inline_kb_subcategories(str(message.from_user.id), category=category.id)
    await bot.send_message(message.from_user.id, text=text, reply_markup=reply_markup)

# получаем комментарий к заказу
@dp.message_handler(state=Form.add_comment)
async def add_comment(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.delete_message(chat_id=-1001810938907, message_id=Form.prev_message.message_id)
    await message.delete()
    order = update_order(id=int(Form.prev_message.text.split('№')[1]), comment=message.text)

    await Form.order_message.edit_text(text=Form.order_message.text + '\n' + message.text, reply_markup=Form.order_message.reply_markup)


# получаем поисковый запрос
@dp.message_handler(state=Form.search)
async def search(message: types.Message, state: FSMContext):
    await state.finish()
    state_category = int(get_user(tg_id=str(message.from_user.id)).state)
    update_user(tg_id=str(message.from_user.id), state=f'{state_category}| {message.text}')
    textReply_markup = inline_kb_listproducts(
        tg_id=str(message.from_user.id), 
        category=state_category, 
        page=[0,5],
        search=message.text
    )
    # последнее сообщение с кнопками
    for item in textReply_markup:
        await asyncio.sleep(1)
        if not item['images']:
            await bot.send_message(
                message.from_user.id,
                text=item['text'], 
                reply_markup=item['reply_markup']
            )
        else:
            try:
                # карточка товара с фото
                images = item['images'].split('\n')
                photo = [types.InputMedia(media=open(img, 'rb'), caption=item['text']) if images.index(img) == 0 else types.InputMedia(media=open(img, 'rb')) for img in images]
                await bot.send_media_group(
                    message.from_user.id, 
                    media=photo,
                )
                # сообщение м кнопками под товаром "добавить в корзину" и тд
                await bot.send_message(
                    message.from_user.id,
                    text = 'Выберите действие: ',
                    reply_markup=item['reply_markup']
                )
                #await asyncio.sleep(0.5)
            except:
                continue
