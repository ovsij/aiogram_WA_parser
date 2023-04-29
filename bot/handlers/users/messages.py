from aiogram import types
from aiogram.dispatcher import FSMContext
import time
import re

from loader import bot, dp, Form

from database.crud import *
from database.models import *
from keyboards.inline import *
from keyboards.reply import *
from keyboards.constructor import InlineConstructor


@dp.message_handler()
async def user_message(message: types.Message):
    await message.delete()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.user_phone)
#@dp.message_handler(content_types=types.Message, state=Form.user_phone)
async def change_phone(message: types.Message, state: FSMContext):
    # записываем номер телефона
    update_user(tg_id=str(message.from_user.id), phone=message.contact.phone_number)
    await state.finish()
    # удаляем ненужные сообщения
    time.sleep(1)
    await message.delete()
    types.ReplyKeyboardRemove()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    # обновляем текст сообщения с меню "настройки"
    try:
        text, reply_markup = inline_kb_settings(message.from_user)
        await Form.menu_message.edit_text(
                    text=text,
                    reply_markup=reply_markup
                )
    except:
        pass

@dp.message_handler(state=Form.user_phone)
async def user_message(message: types.Message):
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    
    _, reply_markup = reply_kb_change(param='phone')
    Form.prev_message = await bot.send_message(
                message.from_user.id, 
			    text='К сожалению, ввести номер телефона текстом не получится. Нажмите на кнопку "Поделиться номером телефона. \nЕсли вы не видите кнопку, нажмите за значек слева от микрофона внизу экрана, тогда кнопка появится',
                reply_markup=reply_markup
            )
    

@dp.message_handler(state=Form.user_address)
async def change_address(message: types.Message, state: FSMContext):
    # записываем номер телефона
    update_user(tg_id=str(message.from_user.id), address=message.text)
    await state.finish()
    # удаляем ненужные сообщения
    time.sleep(1)
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    # обновляем текст сообщения с меню "настройки"
    try:
        text, reply_markup = inline_kb_settings(message.from_user)
        await Form.menu_message.edit_text(
                    text=text,
                    reply_markup=reply_markup
                )
    except:
        pass

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
# получаем промокод от админа
@dp.message_handler(state=Form.addpromocode)
async def add_admin_promocode(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    await Form.addpromocode_discount.set()
    Form.prev_message = await bot.send_message(
            message.from_user.id,
            text=f'Введите размер скидки по промокоду: {message.text}', 
        )

# получаем размер скидки от админа
@dp.message_handler(state=Form.addpromocode_discount)
async def add_admin_promocode_discount(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()
    

    create_promocode(name=Form.prev_message.text.split(': ')[-1], discount=message.text)
    text, reply_markup = inline_kb_addpromocode_catalogs(name=Form.prev_message.text.split(': ')[-1])

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
        update_promocode(name=message.text, tg_id=str(message.from_user.id))
        await bot.send_message(message.from_user.id, f'Промокод {message.text} добавлен в список ваших промокодов')
    else:
        await bot.send_message(message.from_user.id, f'Промокод {message.text} не существует')


# получаем название новой категории
@dp.message_handler(state=Form.add_category)
async def add_category(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()
    if not category_exists(name=message.text):
        create_category(name=message.text, custom=True)
    text, reply_markup = inline_kb_categories(str(message.from_user.id))
    await bot.send_message(message.from_user.id, text=text, reply_markup=reply_markup)
