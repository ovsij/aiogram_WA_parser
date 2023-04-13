from aiogram import types
from aiogram.utils import markdown
from emoji import emojize
from dotenv import load_dotenv
import os

load_dotenv()

from .buttons import *
from .constructor import InlineConstructor
from bot.loader import bot
from database.crud import *


def inline_kb_menu(telegram_user):
    user = get_user(telegram_user)
    # исключаем None
    last_name = [last_name for last_name in [user.last_name, ' '] if last_name][0]
    phone = [phone for phone in [user.phone, '\n--укажите в настройках--'] if phone][0]
    address = [address for address in [user.address, '\n--укажите в настройках--'] if address][0]
    text = markdown.text(
        'ГЛАВНОЕ МЕНЮ',
        'Добро пожаловать в службу оформления онлайн заказов кафе "Темпура".',
        'Вы можете посмотреть наше меню в каталоге и добавить желаемые позиции в корзину.',
        'Мы доставим заказ по вашему адресу или вы можете забрать его сами по адресу: 3-я улица Строителей, 25, офис 11',
        f'\nИмя: \n{user.first_name} {last_name}',
        f'\nТелефон: {phone}',
        f'\nАдрес доставки: {address}',
        sep='\n')

    text_and_data = [
        [emojize(':closed_book: Каталог', language='alias'), 'btn_catalog_1'],
        [emojize(':telephone: Контакты', language='alias'), 'btn_contact'],
        [emojize(':question: Условия', language='alias'), 'btn_terms'],
        [emojize(':gear: Настройки', language='alias'), 'btn_settings'],
    ]
    schema = [1, 2, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_categories(page : int = 1):
    #выводит названия категорий, если их нет выводит продукты
    text = 'КАТАЛОГ'
    categories = get_categories()
    text_and_data = []
    schema = []
    if bool(categories):
        text += '\n\nВыберите категорию'
        for cat in categories:
            text_and_data.append([f'{cat.name}', f'btn_category_{cat.id}_1'])
            schema.append(1)
        
        if len(categories) > 10:
            text_and_data, schema = btn_prevnext(len(categories), text_and_data, schema, page, name='catalog')
        
        text_and_data.append(btn_back('menu'))
        schema.append(1)
        inline_kb = InlineConstructor.create_kb(text_and_data, schema)
        return text, inline_kb
    else:
        return inline_kb_products()
    
def inline_kb_subcategories(category : int = None, page : int = 1):
    #выводит названия суб-категорий, если их нет выводит продукты
    text = f'КАТАЛОГ\n\n{get_category(id=category).name}'
    sub_categories = get_subcategory(category_id=category)
    text_and_data = []
    schema = []
    if sub_categories:
        for sc in sub_categories:
            text_and_data.append([f'{sc.name}', f'btn_subcategory_{category}_{sc.id}_1'])
            schema.append(1)
        if len(sub_categories) > 10:
            text_and_data, schema = btn_prevnext(len(sub_categories), text_and_data, schema, page, name=f'category_{category}')

        text_and_data.append(btn_back(f'catalog_1'))
        schema.append(1)
        
        inline_kb = InlineConstructor.create_kb(text_and_data, schema)
        return text, inline_kb
    else:
        return inline_kb_products(category=category, page=page)
    
def inline_kb_products(tg_id : str, category : int = None, sub_category : int = None, page : int = 1):
    text = 'КАТАЛОГ'
    if sub_category == None:
        text += f'\n\n{get_category(id=category).name}'
        products = get_product(category_id=category)
        btn_prevnext_name = f'category_{category}'
    else:
        text += f'\n\n{get_subcategory(id=sub_category).name}'
        products = get_product(category_id=category, subcategory_id=sub_category)
        btn_prevnext_name = f'subcategory_{category}_{sub_category}'
    
    text_and_data = []
    schema = []
    if bool(products):
        for p in products:
            if p.deleted:
                if tg_id in os.getenv('ADMINS'):
                    text_and_data.append([emojize(f':x: {p.name}', language='alias'), f'btn_product_{p.id}'])
            elif p.edited:
                if tg_id in os.getenv('ADMINS'):
                    text_and_data.append([emojize(f':recycle: {p.name}', language='alias'), f'btn_product_{p.id}'])
                else:
                    text_and_data.append([f'{p.name}', f'btn_product_{p.id}'])
            else:
                text_and_data.append([f'{p.name}', f'btn_product_{p.id}'])
            schema.append(1)
    else:
        text += '\n\n К сожалению, на данный момент в этой категории ничего нет'
    if len(products) > 10:
        text_and_data, schema = btn_prevnext(len(products), text_and_data, schema, page, name=btn_prevnext_name)
    if sub_category == None:
        text_and_data.append(btn_back(f'catalog_1'))
    else:
        text_and_data.append(btn_back(f'category_{category}_1'))
    schema.append(1)
    
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_product(tg_id : str, id : int, counter : int = 1):
    product = get_product(id=id)
    if not product.subcategory:
        products = get_product(category_id=product.category.id)
    else:
        products = get_product(category_id=product.category.id, subcategory_id=product.subcategory.id)
    
    description = product.description
    description = '' if not product.description else product.description
    price = 'Не указана' if not product.price else f'{product.price} руб.'
    text = f'{product.name}\n\n{description}\n\nЦена: {price}'
    if tg_id in os.getenv('ADMINS'):
        products_id = [p.id for p in products]
    else:
        print('del')
        products_id = [p.id for p in products if not p.deleted]
    back = products_id[products_id.index(id) - 1]
    if products_id.index(id) == len(products) - 1:
        next = products_id[0]
    else:
        next = products_id[products_id.index(id) + 1]
    if not product.subcategory:
        btn_back = f'btn_category_{product.category.id}_1'
    else:
        btn_back = f'btn_subcategory_{product.category.id}_{product.subcategory.id}_1'
    text_and_data = [
        [emojize(':arrow_backward:', language='alias'), f'btn_product_{back}'],
        [f'[{products_id.index(id) + 1} из {len(products)}]', f'btn_pass'],
        [emojize(':arrow_forward:', language='alias'), f'btn_product_{next}'],
    ]
    schema = [3]
    # добавить кнопку "удалить товар"
    if tg_id in os.getenv('ADMINS'):
        if product.deleted:
            text =  emojize(':x: ', language='alias') + text
            text_and_data.append(['Восстановить товар', f'btn_returnproduct_{id}'])
        else:
            text_and_data.append(['Удалить товар', f'btn_delproduct_{id}'])
        
        text_and_data.append(['Изменить товар', f'btn_editproduct_{id}'])
        schema.append(1)
        schema.append(1)
    # добавить кнопку назад
    text_and_data.append([emojize(':leftwards_arrow_with_hook: Назад', language='alias'), btn_back])
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_editproduct(product_id):
    text = 'Выберите, что бы вы хотели изменить.'
    text_and_data = [
        ['Наименование', f'btn_editproduct_name_{product_id}'],
        ['Описание', f'btn_editproduct_description_{product_id}'],
        ['Цена', f'btn_editproduct_price_{product_id}'],
    ]
    schema = [1, 1, 1]
    if get_product(id=product_id).edited:
        text_and_data.append(['Очистить изменения', f'btn_uneditproduct_{product_id}'])
        schema.append(1)
    text_and_data.append(btn_back(f'product_{product_id}'))
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb


async def inline_kb_cart(telegram_user):
    text = 'КОРЗИНА\n'
    text_and_data = []
    schema = []
    cart = get_cart(telegram_user)
    prices = []
    sum = 0
    for p in cart:
        product = get_product_by_id(p.product.id)
        sum += product.price * p.count
        text += f'\n{cart.index(p) + 1}. {product.name} \n    ({round(product.price, 2)} р. * {p.count} шт.)'
        text_and_data.append([emojize(f':x: {product.name} | {p.count} шт.', language='alias'), f'btn_delete_{p.id}'])
        schema.append(1)
        prices.append(types.LabeledPrice(label=f'{product.name} | {p.count} шт.', amount=int(product.price * p.count * 100)))
    
    if not cart:
        text += '\nКорзина пуста...'
        button_type = None
    else:
        text += f'\n\nИтого: {round(sum, 2)} руб.'
        text_and_data.append([emojize(f':x: Очистить корзину', language='alias'), f'btn_deleteall'])
        schema.append(1)
        button_type = []
        for i in range(len(text_and_data)):
            button_type.append('callback_data')
        link = await bot.create_invoice_link(title='Заказ', description='Оформление заказа', payload='test',
            provider_token=os.getenv('provider_token'), currency='rub', 
            prices=prices, 
            need_name=True, need_phone_number=True, need_email=True, need_shipping_address=True)
        text_and_data.append([emojize(f':white_check_mark: Оформить заказ', language='alias'), link])
        button_type.append('url')
        schema.append(1)
        button_type.append('callback_data')
    
    text_and_data.append([emojize(':leftwards_arrow_with_hook: В меню', language='alias'), 'btn_menu'])
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema, button_type)
    return text, inline_kb

def inline_kb_orders(telegram_user, page : int):
    text = 'ИСТОРИЯ ЗАКАЗОВ'
    orders = get_orders(tg_id=str(telegram_user.id))
    if not orders:
        text += '\n\nВы еще ничего не заказывали...'
    text_and_data = []
    schema = []
    for order in orders:
        if order.status == 'Доставлен':
            emoji_status = ':white_check_mark:'
        elif order.status == 'Отменен':
            emoji_status = ':x:'
        elif order.status == 'В обработке':
            emoji_status = ':recycle:'
        text_and_data.append([emojize(f'{order.datetime.date()} {emoji_status} {order.status}', language='alias'),f'btn_order_{order.id}_{page}'])
        schema.append(1)
    if len(orders) > 10:
        text_and_data, schema = btn_prevnext(len(orders), text_and_data, schema, page, 'orders')
    text_and_data.append([emojize(':leftwards_arrow_with_hook: В меню', language='alias'), 'btn_menu'])
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_order(telegram_user : dict, id : int, page : int):
    order = get_order(id=id)
    text = markdown.text(
        f'ЗАКАЗ № {id}',
        '\n'
        f'Дата:                 {order.datetime.date()}',
        f'Время:              {order.datetime.strftime("%H:%M")}',
        f'Вид доставки: {order.delivery_type}',
        f'Вид оплаты:     {order.payment_type}',
        f'Статус:              {order.status}\n\n', 
        'Содержимое заказа:\n', sep='\n')
    products = get_products_by_order(order)
    counter = 1
    sum = 0
    for p in products:
        product = get_product_by_id(id=p.product.id)
        text += f'{counter}. {product.name} \n    ({round(product.price, 2)} р. * {p.count} шт.)\n'
        counter += 1
        sum += product.price * p.count
    text += f'\nИтого: {round(sum, 2)} руб.'
    text_and_data = [
        [emojize(':arrow_backward: К заказам', language='alias'), f'btn_orders_{page}'],
        [emojize(':leftwards_arrow_with_hook: В меню', language='alias'), 'btn_menu']
    ]
    schema = [1, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_terms(tg_id):
    text = markdown.text(
        'УСЛОВИЯ ДОСТАВКИ И ОПЛАТЫ',
        '',
        'Мы работаем каждый день с 10:00 до 20:00',
        'Вы можете оплатить заказ как через телеграм оплату, так и наличными при самовывозе',
        '',
        'Контактный телефон:',
        '8800xxxxxxxxx',
        sep='\n'
    )
    text_and_data = [
        btn_back('menu')
    ]
    schema = [1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_contact():
    text = markdown.text(
        'КОНТАКТЫ',
        'У нас можно заказать бота для:',
        '- Магазинов оптовой и розничной торговли',
        '- Кафе, кондитерских и фастфудов',
        '- Онлайн и офлайн бизнеса',
        '- Любые иные цели по вашему запросу',
        '',
        'Мы предоставляем:',
        '- Удобное меню бота',
        '- Походящий формат административной панели',
        '- Индивидуальный подход к каждому клиенту',
        '- Предсказуемые сроки работы',
        sep='\n'
        )
    text_and_data = [
        ['Заказать бота', 't.me/v3talik'],
        btn_back('menu')
    ]
    schema = [1, 1]
    button_type = ['url', 'callback_data']
    inline_kb = InlineConstructor.create_kb(text_and_data, schema, button_type)
    return text, inline_kb

def inline_kb_settings(telegram_user):
    user = get_user(telegram_user)
    # исключаем None
    last_name = [last_name for last_name in [user.last_name, ' '] if last_name][0]
    phone = [phone for phone in [user.phone, '\n--укажите в настройках--'] if phone][0]
    address = [address for address in [user.address, '\n--укажите в настройках--'] if address][0]
    text = markdown.text(
        'НАСТРОЙКИ',
        f'\nИмя: \n{user.first_name} {last_name}',
        f'\nТелефон: {phone}',
        f'\nАдрес доставки: {address}',
        sep='\n')
    text_and_data = [
        ['Изменить телефон', 'btn_change_phone'],
        ['Изменить адрес', 'btn_change_address'],
        btn_back('menu')
    ]
    schema = [1, 1, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_admin():
    text = markdown.text(
        'КАБИНЕТ АДМИНИСТРАТОРА'
    )
    text_and_data = [
        ['Рассылка', 'btn_sendmessage'],
        ['Добавить каталог', 'btn_addcatalog'],
        ['Удалить каталог', 'btn_delcatalog'],
        ['Редактировать каталог', 'btn_editcatalog'],
        ['Добавить товар', 'btn_additem'],
        ['Удалить товар', 'btn_delitem'],
        ['Запустить обновление каталогов', 'btn_updatecatalog'],
        btn_back('menu')
    ]
    schema = [1, 1, 1, 1, 1, 1, 1, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

# проверка сообщения перед отправкой
def inline_sendmessage():
    text_and_data = [
        [emojize(':white_check_mark: Отправить :white_check_mark:', language='alias'), 'aceptsending'],
        [emojize(':x: Отменить :x:', language='alias'), 'denysending']
    ]
    schema = [1, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return inline_kb

def inline_kb_delcatalog():
    text = 'Выберите каталог, который хотите удалить'
    text_and_data = []
    schema = [1]
    catalogs = get_catalogs()
    for catalog in catalogs:
        text_and_data.append([emojize(f':recycle: {catalog.phone}', language='alias'), f'btn_delcatalog_{catalog.phone}'])
        schema.append(1)
    text_and_data.append(btn_back('admin'))
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_editcatalog():
    text = 'Выберите каталог, наценку которого хотите изменить'
    text_and_data = []
    schema = [1]
    catalogs = get_catalogs()
    for catalog in catalogs:
        text_and_data.append([emojize(f':recycle: {catalog.phone} | {catalog.margin}%', language='alias'), f'btn_editcatalog_{catalog.phone}'])
        schema.append(1)
    text_and_data.append(btn_back('admin'))
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

# выбор каталога для обновления
def inline_kb_updatecatalog():
    text = 'Выберите каталог, который хотите обновить'
    text_and_data = []
    schema = [1]
    catalogs = get_catalogs()
    for catalog in catalogs:
        if catalog.phone == 'valentino':
            name = get_category(catalog_id=catalog.id).name
            text_and_data.append([emojize(f':recycle: {name}', language='alias'), f'btn_updateVALENTINO'])
            schema.append(1)
        elif catalog.phone == 'lesilla':
            name = get_category(catalog_id=catalog.id).name
            text_and_data.append([emojize(f':recycle: {name}', language='alias'), f'btn_updateLESILLA'])
            schema.append(1)
        else:
            try:
                name = get_category(catalog_id=catalog.id).name
            except:
                name = catalog.phone
            text_and_data.append([emojize(f':recycle: {name}', language='alias'), f'btn_updatecatalog_{catalog.phone}'])
            schema.append(1)
    text_and_data.append(btn_back('admin'))
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_approveupdatecapalog(phone : str = None, custom : str = None):
    if phone:
        text = f'Вы уверены, что хотите запустить обновление каталога {phone}?\nЭто действие удалит все товары из этого каталога и загрузит обновленные данные'
        text_and_data = [
            [emojize(':white_check_mark: Обновить :white_check_mark:', language='alias'), f'btn_updatecatalog_{phone}_accept'],
            [emojize(':x: Отменить :x:', language='alias'), f'btn_updatecatalog_{phone}_deny']
        ]
    if custom:
        text = f'Вы уверены, что хотите запустить обновление каталога {custom}?\nЭто действие удалит все товары из этого каталога и загрузит обновленные данные'
        text_and_data = [
            [emojize(':white_check_mark: Обновить :white_check_mark:', language='alias'), f'btn_update{custom}_accept'],
            [emojize(':x: Отменить :x:', language='alias'), f'btn_update{custom}_deny']
        ]
    schema = [1, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb