from aiogram import types
from aiogram.dispatcher import FSMContext
import time

from loader import bot, dp, Form

from database.crud import *
from database.models import *
from keyboards.inline import *
from keyboards.reply import *

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
async def add_catalog(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()
    text = 'Пришлите номер аккаунта в котором находится каталог в формате: 393421807916\n\n Номер телефона должен состоять из 12 цифр без пробелов и иных знаков'
    Form.prev_message = await bot.send_message(
            message.from_user.id,
            text=text,
            )

# получаем номер телефона для добавления каталога
@dp.message_handler(state=Form.add_catalog)
async def add_catalog(message: types.Message, state: FSMContext):

    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    #text, reply_markup = inline_kb_admin()
    

    if not catalog_exists(phone=message.text):
        phone = message.text
        link = 'https://web.whatsapp.com/catalog/' + message.text
        create_catalog(phone=phone, link=link)
        text = 'Пришлите какой процент наценки будет у этого каталога (двузначное число). Например: 20'
        await Form.add_margin.set()
        Form.add_margin = message.text
        
    else:
        text = f'\n\nКаталог {message.text} уже существует'
    
    Form.prev_message = await bot.send_message(
                message.from_user.id,
                text=text,
                )
    
# неверный формат процента наценки
@dp.message_handler(lambda message: len(message.text) != 2, state=Form.add_margin)
async def add_catalog(message: types.Message, state: FSMContext):
    await message.delete()

# получаем процент наценки каталога
@dp.message_handler(state=Form.add_margin)
async def add_catalog(message: types.Message, state: FSMContext):

    await state.finish()
    await bot.delete_message(chat_id=message.chat.id, message_id=Form.prev_message.message_id)
    await message.delete()

    #phone = get_catalog(id=max([c.id for c in get_catalogs()])).phone
    phone = Form.add_margin
    update_catalog(phone=phone, margin=int(message.text))
    await state.clear()
    text, reply_markup = inline_kb_admin()
    text += f'\n\nКаталог добавлен'
    await bot.send_message(
                message.from_user.id,
                text=text,
                reply_markup=reply_markup
                )



@dp.message_handler()
async def user_message(message: types.Message):
    await message.delete()
