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
        'ГЛАВНОЕ МЕНЮ:',
        '',
        emojize('Всем привет! На связи Concierge Shopping:heart_hands: Мы - удобный сервис выкупа и доставки товаров самых известных брендов, найдем ту самую вещь из твоего виш листа', language='alias'),
        '',
        'Вы можете ознакомиться с нашим каталогом, а если вы не нашли то, что вам нужно-присылайте фото желаемой вещи в сообщения, а наши байеры выкупят ее для Вас по самой лучшей цене',
        sep='\n')

    text_and_data = [
        [emojize(':closed_book: Каталог', language='alias'), 'btn_catalog_1'],
        [emojize(':shopping_cart: Корзина', language='alias'), 'btn_cart_0-5'],
        [emojize(':package: Как сделать заказ', language='alias'), 'btn_howto'],
        [emojize(':question: Условия', language='alias'), 'btn_terms'],
        [emojize(':telephone: Контакты', language='alias'), 'btn_contact'],
        [emojize(':bust_in_silhouette: Личный кабинет', language='alias'), 'btn_lk']
    ]
    schema = [1, 1, 1, 2, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_categories(tg_id : str, page : int = 1):
    #выводит названия категорий, если их нет выводит продукты
    text = 'КАТАЛОГ'
    categories = get_category()
    text_and_data = []
    schema = []
    if bool(categories):
        text += '\n\nВыберите категорию'
        for cat in categories:
            text_and_data.append([f'{cat.name}', f'btn_category_{cat.id}_1'])
            schema.append(1)
        
        if len(categories) > 30:
            text_and_data, schema = btn_prevnext(len(categories), text_and_data, schema, page, name='catalog')
        
        if tg_id in os.getenv('ADMINS'):
            text_and_data.append(['Добавить категорию', 'btn_addcategory'])
            schema.append(1)

        text_and_data.append(btn_back('menu'))
        schema.append(1)
        inline_kb = InlineConstructor.create_kb(text_and_data, schema)
        return text, inline_kb
    else:
        text += '\n\n К сожалению, на данный момент в каталоге ничего нет'
        text_and_data = []
        schema = []
        if tg_id in os.getenv('ADMINS'):
            text_and_data.append(['Добавить категорию', 'btn_addcategory'])
            schema.append(1)
        text_and_data.append(btn_back('menu'))
        schema.append(1)
        inline_kb = InlineConstructor.create_kb(text_and_data, schema)
        return text, inline_kb
    
def inline_kb_subcategories(tg_id : str, category : int = None, page : int = 1):
    #выводит названия суб-категорий, если их нет выводит продукты
    category_name = get_category(id=category).name
    text = f'КАТАЛОГ\n\n{category_name}'
    sub_categories = get_subcategory(category_id=category)
    text_and_data = []
    schema = []
    if sub_categories:
        for sc in sub_categories:
            text_and_data.append([f'{sc.name}', f'btn_ls_{category}_{sc.id}_s=_p=_n_0-5'])
            schema.append(1)
        if len(sub_categories) > 30:
            text_and_data, schema = btn_prevnext(len(sub_categories), text_and_data, schema, page, name=f'category_{category}')

        if get_category(id=category).name == 'LeSILLA':
            text_and_data.append([emojize(':scissors: Таблица размеров', language='alias'), f'btn_sizes_{category}'])
            schema.append(1)

        if tg_id in os.getenv('ADMINS'):# and get_category(id=category).custom:
            text_and_data.append([f'Удалить категорию {category_name}', f'btn_deletecategory_{category}'])
            schema.append(1)
            text_and_data.append(['Добавить подкатегорию', f'btn_addsubcategory_{category}'])
            schema.append(1)
        text_and_data.append(btn_back(f'catalog_1'))
        schema.append(1)
        
        inline_kb = InlineConstructor.create_kb(text_and_data, schema)
        return text, inline_kb
    else:
        text_and_data = []
        if tg_id in os.getenv('ADMINS'):
            text_and_data.append([f'Удалить категорию {category_name}', f'btn_deletecategory_{category}'])
            schema.append(1)
            text_and_data.append(['Добавить подкатегорию', f'btn_addsubcategory_{category}'])
            schema.append(1)
        text_and_data.append(btn_back(f'catalog_1'))
        schema.append(1)
        text = 'К сожалению, в данной категории пока ничего нет'
        inline_kb = InlineConstructor.create_kb(text_and_data, schema)
        return text, inline_kb
        #return inline_kb_listproducts(tg_id=tg_id, category=category, page=page)

def inline_kb_listproducts(tg_id : str, category : int = None, sub_category : int = None, sizes : str = None, prices : str = None, page : list = [0, 5], back : bool = False, sort : str = None):
    textInline_kb = []
    if sizes or prices:
        products = get_product(category_id=category, subcategory_id=sub_category, sizes=sizes, prices=prices, sort=sort)
    else:
        products = get_product(category_id=category, subcategory_id=sub_category, sort=sort)
    if len(products) == 0:
        text_and_data = []
        schema = []
        if tg_id in os.getenv('ADMINS'):
            text_and_data.append(['Удалить подкатегорию', f'btn_deletesubcategory_{category}_{sub_category}'])
            schema.append(1)
            text_and_data.append(['Добавить товар', f'btn_addproduct_{category}_{sub_category}'])
            schema.append(1)

        text_and_data.append(btn_back('menu'))
        schema.append(1)

        text = 'К сожалению, в данной подкатегории пока ничего нет'
        reply_markup = InlineConstructor.create_kb(text_and_data, schema)
        return [{'text' : text, 'reply_markup' : reply_markup, 'images' : False}]
    
    # показываем удаленные товары только админам
    if tg_id in os.getenv('ADMINS'):
        products = [p for p in products]
    else:
        products = [p for p in products if not p.deleted]

    # формируем список товаров 5 или 10 в соответствии с выбором пользователя
    for product in products[page[0]:page[1]]:
        dct = {}
        description = product.description
        description = '' if not product.description else product.description
        price = 'Не указана' if not product.price else product.price
        dct['text'] = f'{product.name}\n\nАртикул: {product.article}\n{description}\n\nЦена: {price} руб.'
        promocode = get_promocode(tg_id=tg_id, category_id=category)
    
        if promocode and price != 'Не указана':
            dct['text'] += f'\n\nСо скидкой по промокоду:\n{int(get_promoprice(product=product, tg_id=tg_id))} руб'
        if cart_exists(tg_id=tg_id, product_id=product.id):
            text_and_data = [
                [emojize('Удалить из корзины', language='alias'), f'btn_delfromcart_{product.id}']
            ]
        else:
            text_and_data = [
                [emojize('Добавить в корзину', language='alias'), f'btn_tocart_{product.id}']
            ]
        schema = [1]
        # добавить кнопку "удалить товар"
        if tg_id in os.getenv('ADMINS'):
            if product.deleted:
                dct['text'] =  emojize(':x: ', language='alias') + dct['text']
                text_and_data.append(['Восстановить товар', f'btn_returnproduct_{product.id}'])
                schema.append(1)
            if product.edited:
                dct['text'] =  emojize(':recycle: ', language='alias') + dct['text']
            else:
                text_and_data.append(['Удалить товар', f'btn_delproduct_{product.id}'])
                schema.append(1)
            text_and_data.append(['Изменить товар', f'btn_editproduct_{product.id}'])
            
            schema.append(1)
        
        dct['reply_markup'] = InlineConstructor.create_kb(text_and_data, schema)
        dct['images'] = product.image
        textInline_kb.append(dct)
    len_prodcts = page[1] if len(textInline_kb) >= 5 else len(products)
    sizes_code = f'_s={sizes}' if sizes else '_s='
    filter_size_emoji = ':white_check_mark:' if len(sizes_code) > 3 else ''
    prices_code = f'_p={prices}' if prices else '_p='
    filter_price_emoji = ':white_check_mark:' if len(prices_code) > 3 else ''
    filter_pricedown_emoji = ':white_check_mark:' if sort == 'd' else ''
    filter_priceup_emoji = ':white_check_mark:' if sort == 'u' else ''
    sort = f'{sort}_' if sort else ''
    page_0 = 0 if back else page[1]
    page_5 = 5 if back else page[1] + 5
    page_10 = 10 if back else page[1] + 10
    text_and_data = [
        [emojize(f'{filter_size_emoji} Фильтр по размеру', language='alias'), f'btn_sf_{category}_{sub_category}{sizes_code}{prices_code}_n'],
        [emojize(f'{filter_price_emoji} Фильтр по цене', language='alias'), f'btn_pf_{category}_{sub_category}{sizes_code}{prices_code}_n'],
        [emojize(f'{filter_priceup_emoji} По возрастанию цены', language='alias'), f'btn_ls_{category}_{sub_category}{sizes_code}{prices_code}_u_0-5'],
        [emojize(f'{filter_pricedown_emoji} По убыванию цены', language='alias'), f'btn_ls_{category}_{sub_category}{sizes_code}{prices_code}_d_0-5'],
        [emojize('Открыть списком', language='alias'), f'btn_subcategory_{category}_{sub_category}_1'],
        [emojize(':shopping_cart: Перейти в корзину', language='alias'), 'btn_cart_0-5'],
        [emojize(':arrow_down_small: Eще 5 товаров :arrow_down_small:', language='alias'), f'btn_ls_{category}_{sub_category}{sizes_code}{prices_code}_{sort}{page_0}-{page_5}'],
        [emojize(':arrow_down_small: Eще 10 товаров :arrow_down_small:', language='alias'), f'btn_ls_{category}_{sub_category}{sizes_code}{prices_code}_{sort}{page_0}-{page_10}'],
        btn_back(f'category_{category}_1')
    ]
    schema = [1, 1, 1, 1, 1, 1, 1, 1, 1]
    if tg_id in os.getenv('ADMINS') and get_category(id=category).custom:
        text_and_data.insert(7, ['Добавить товар', f'btn_addproduct_{category}_{sub_category}'])
        schema.append(1)
        text_and_data.insert(8, [f'Удалить подкатегорию {get_subcategory(id=sub_category).name}', f'btn_deletesubcategory_{category}_{sub_category}'])
        schema.append(1)
    textInline_kb.append(
        {
        'text' : f'{get_category(id=category).name}\n{get_subcategory(id=sub_category).name}\n\nПоказано {len_prodcts} товаров из {len(products)}',
        'reply_markup' : InlineConstructor.create_kb(text_and_data, schema),
        'images' : False
        }
    )
    
    return textInline_kb
def inline_kb_tocart(product_id : int, sizes : list = []):
    text = 'Выберите размер, который хотите добавить в корзину'
    text_and_data = []
    schema = []
    product = get_product(id=product_id)
    for size in product.sizes.split(', '):
        if size in sizes:
            sizes_emoji = ':white_check_mark:'
            sizes_code = '_s='
            new_sizes = [s for s in sizes]
            new_sizes.remove(size)
            for ns in new_sizes:
                sizes_code += ns + '-'
            sizes_code = sizes_code.strip('-')
        else:
            sizes_emoji = ''
            sizes_code = '_s='
            new_sizes = [s for s in sizes]
            new_sizes.append(size)
            for ns in new_sizes:
                sizes_code += ns + '-'
            sizes_code = sizes_code.strip('-')
        text_and_data.append([emojize(f'{sizes_emoji} {size}', language='alias'), f'btn_tocart_{product.id}{sizes_code}'])
    for _ in range(len(text_and_data) // 4):
        schema.append(4)
    if len(text_and_data) % 4 > 0:
        schema.append(len(text_and_data) % 4)
   
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb  

def inline_kb_sizefilter(category : int = None, sub_category : int = None, sizes_code_list : list = None, prices_code_list : list = None, page : list = None, sort : str = None):
    text = "Выберите один или несколько размеров из доступных для данной категории товаров\n\nМаксимум можно выбрать 6 размеров"
    text_and_data = []
    schema = []
    all_sizes = []
    for product in get_product(category_id=category, subcategory_id=sub_category, sort=sort):
        all_sizes += str(product.sizes).split(', ')
    if 'S' in all_sizes or 'M' in all_sizes or 'L' in all_sizes or 'XL' in all_sizes or '2XL' in all_sizes or '3XL' in all_sizes or '4XL' in all_sizes or '5XL' in all_sizes:
        standart_sizes = ['S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']
        for st_size in ['S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']:
            if st_size not in all_sizes:
                standart_sizes.remove(st_size)
        all_sizes = standart_sizes
    else:
        all_sizes = list(set(all_sizes))
        sorted_list = []
        for size in all_sizes:
            if len(size) > 0:
                try:
                    sorted_list.append(float(size))
                except:
                    continue
        sorted_list.sort()
        all_sizes = [str(fl_size).replace('.0', '') for fl_size in sorted_list]
    prices_code = 'p='
    for price in prices_code_list:
        prices_code += price + '-'
    prices_code = prices_code.strip('-')
    if sizes_code_list:
        for size_ in all_sizes:
            new_sizes = []        
            if size_ in sizes_code_list:
                sizes_code = 's='
                new_sizes = [size for size in sizes_code_list]
                new_sizes.remove(size_)
                for s in new_sizes:
                    sizes_code += s + '-'
                sizes_code = sizes_code.strip('-')
                text_and_data.append(
                    [emojize(f':white_check_mark: {size_}', language='alias'), f'btn_sf_{category}_{sub_category}_{sizes_code}_{prices_code}_n']
                )
            elif size_ not in sizes_code_list:
                sizes_code = 's='
                new_sizes = [size for size in sizes_code_list]
                new_sizes.append(size_)
                for s in new_sizes:
                    sizes_code += s + '-'
                sizes_code = sizes_code.strip('-')
                text_and_data.append(
                    [emojize(f'{size_}', language='alias'), f'btn_sf_{category}_{sub_category}_{sizes_code}_{prices_code}_n']
                )
        next_size_code = ''
        for sze in sizes_code_list:
            next_size_code += sze + '-'
        next_size_code = next_size_code.strip('-')
    else:
        for size_ in all_sizes:
            sizes_code = f's={size_}'
            text_and_data.append(
                    [emojize(f'{size_}', language='alias'), f'btn_sf_{category}_{sub_category}_{sizes_code}_{prices_code}_n']
                )
        next_size_code = ''
    schema = []
    if len(text_and_data) % 3 == 0:
        for _ in range(int(len(text_and_data)/3)):
            schema.append(3)
    else:
        for _ in range(len(text_and_data)//3):
            schema.append(3)
        schema.append(len(text_and_data) - sum(schema))
    page = [0, 5] if not page else page
    text_and_data.append([emojize(':arrow_backward: Назад', language='alias'), f'btn_ls_{category}_{sub_category}_s={next_size_code}_{prices_code}_{page[0]}-{page[1]}_back'])
    text_and_data.append([emojize(':arrow_down_small: Применить :arrow_down_small:', language='alias'), f'btn_ls_{category}_{sub_category}_s={next_size_code}_{prices_code}_n_0-5'])
    schema.append(2)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb            

def inline_kb_pricefilter(category : int = None, sub_category : int = None, sizes_code_list : list = None, prices : list = None, page : list = [0, 5]):
    text = "Выберите один или несколько диапазонов"
    text_and_data = []
    schema = []
    diapazon_list = [
        {'name' : 'до 10000 р.', 'id' : '1'}, 
        {'name' : '10000 р. - 20000 р.', 'id' : '2'}, 
        {'name' : '20000 р. - 50000 р.', 'id' : '3'}, 
        {'name' : 'от 50000 р.', 'id' : '4'}]
    
    prices_code = ''
    if prices:
        for price in prices:
            prices_code += price + '-'
    prices_code = prices_code.strip('-')
    # добавляем размеры
    sizes_code = ''
    if sizes_code_list:
        for code in sizes_code_list:
            sizes_code += code + '-'
        sizes_code = sizes_code.strip('-')

    for code in diapazon_list:
        if prices:
            price_emoji = ':white_check_mark: ' if code['id'] in prices else ''
        else:
            price_emoji = ''

        button_pcode = prices_code
        if code['id'] in button_pcode:
            button_pcode = button_pcode.replace(code['id'], '').replace('--', '-')
        else:
            button_pcode += '-' + code['id']
            button_pcode = button_pcode.strip('-')
        text_and_data.append([emojize(f'{price_emoji}{code["name"]}', language='alias'), f'btn_pf_{category}_{sub_category}_s={sizes_code}_p={button_pcode}'])
        
        #text_and_data.append([emojize(f'{price_emoji}{code["name"]}', language='alias'), f'btn_pf_{category}_{sub_category}_p={prices_code}'])
        schema.append(1)
    text_and_data.append([emojize(':arrow_backward: Назад', language='alias'), f'btn_ls_{category}_{sub_category}_s={sizes_code}_p={prices_code}_{page[0]}-{page[1]}_back'])
    text_and_data.append([emojize(':arrow_down_small: Применить :arrow_down_small:', language='alias'), f'btn_ls_{category}_{sub_category}_s={sizes_code}_p={prices_code}_0-5'])
    schema.append(2)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb   

# при открытии списком субкатегории
def inline_kb_products(tg_id : str, category : int = None, sub_category : int = None, page : int = 1):
    text = 'КАТАЛОГ'
    if sub_category == None:
        text += f'\n\n{get_category(id=category).name}'
        products = get_product(category_id=category)
        btn_prevnext_name = f'category_{category}'
    else:
        text += f'\n\n{get_subcategory(id=sub_category).name}'
        products = get_product(category_id=category, subcategory_id=sub_category, sort='n')
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
    if len(products) > 30:
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
        products = get_product(category_id=product.category.id, subcategory_id=product.subcategory.id, sort='n')
    
    description = product.description
    description = '' if not product.description else product.description
    price = 'Не указана' if not product.price else product.price
    text = f'{product.name}\n\nАртикул: {product.article}\n{description}\n\nЦена: {price} руб.'
    try:
        promocode_id = get_user_promocode(tg_id=tg_id)
        promocode = get_promocode(id=promocode_id)
    except:
        promocode = False
    if promocode:
        promo_price = int(price) - (int(price) / 100 * promocode.discount)
        text += f'\n\nСо скидкой по промокоду {promocode.name}:\n{int(promo_price)} руб'
    if tg_id in os.getenv('ADMINS'):
        products_id = [p.id for p in products]
    else:
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
    # добавить кнопку в главное меню
    text_and_data.append([emojize(':leftwards_arrow_with_hook: В главное меню', language='alias'), 'btn_menu'])
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
        ['Размеры', f'btn_editproduct_sizes_{product_id}'],
        ['Цена', f'btn_editproduct_price_{product_id}'],
        ['Изображения', f'btn_editproduct_images_{product_id}']
    ]
    schema = [1, 1, 1, 1, 1]
    if get_product(id=product_id).edited:
        text_and_data.append(['Очистить изменения', f'btn_uneditproduct_{product_id}'])
        schema.append(1)
    text_and_data.append(btn_back(f'product_{product_id}'))
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

async def inline_kb_cart(tg_id : str, page : list = [0, 5]):
    textInline_kb = []
    products = get_cart(tg_id=tg_id)
    for product in products[page[0]:page[1]]:
        dct = {}
        description = '' if not product[0].description else product[0].description.split('\n\nSizes:')[0].split('\n\nРазмеры:')[0]
        description += f"\n\nВыбранные размеры: {product[1].replace('-', ', ')}"
        price = 'Не указана' if not product[0].price else f'{product[0].price} руб.'
        dct['text'] = f'{product[0].name}\n\nАртикул: {product[0].article}\n{description}\n\nЦена: {price}'
        # применяем промокод
        promocode = get_promocode(tg_id=tg_id, category_id=product[0].category.id)
        if promocode and price != 'Не указана':
            dct['text'] += f'\n\nСо скидкой по промокоду:\n{int(get_promoprice(product=product[0], tg_id=tg_id))} руб'

        if cart_exists(tg_id=tg_id, product_id=product[0].id):
            text_and_data = [
                [emojize('Удалить из корзины', language='alias'), f'btn_delfromcart_{product[0].id}']
            ]
        else:
            text_and_data = [
                [emojize('Добавить в корзину', language='alias'), f'btn_tocart_{product[0].id}']
            ]

        dct['reply_markup'] = InlineConstructor.create_kb(text_and_data, [1])
        dct['images'] = product[0].image
        textInline_kb.append(dct)

    len_prodcts = page[1] if len(textInline_kb) >= 5 else len(products)
    text_and_data = [
        [emojize(':shopping_bags: Оформить заказ', language='alias'), f'btn_createorder_0'],
        [emojize(':arrow_down_small: Eще 5 товаров :arrow_down_small:', language='alias'), f'btn_cart_{page[1]}-{page[1] + 5}'],
        [emojize(':arrow_down_small: Eще 10 товаров :arrow_down_small:', language='alias'), f'btn_cart_{page[1]}-{page[1] + 10}'],
        btn_back(f'menu')
    ]
    textInline_kb.append(
        {
        'text' : f'Показано {len_prodcts} товаров из {len(products)}',
        'reply_markup' : InlineConstructor.create_kb(text_and_data, [1, 1, 1, 1]),
        'images' : False
        }
    )
    return textInline_kb

def inline_kb_createorder(tg_id : str, create : bool, order_id : int = None):
    if not create:
        text = 'Состав заказа:'
        products = get_cart(tg_id=tg_id)
        sum = 0
        i = 1
        for product in products:
            price = get_promoprice(product=product[0], tg_id=tg_id)
            text += f'\n\n {i}. {product[0].name} ({product[1]}) - {price} руб.'
            sum += price
            i += 1
        text += f'\n\nИтого: {sum} руб.'
        text += '\n\n**Для оформления заказа нам необходимо знать ваш номер телефона. Если вы не хотите делиться номером, для оформления заказа перешлите сообщения с товарами менеджеру.'
        if not get_user(tg_id=tg_id).phone:
            text_and_data = [
                [emojize(':telephone_receiver: Указать номер телефона', language='alias'), f'btn_phone'],
                btn_back(f'cart')
            ]
            schema = [1, 1]
        elif sum == 0:
            text_and_data = [
                btn_back(f'cart')
            ]
            schema = [1]
        else:
            text_and_data = [
                [emojize(':shopping_bags: Заказать', language='alias'), f'btn_createorder_1'],
                btn_back(f'cart')
            ]
            schema = [1, 1]
    else:
        text = f'Заказ оформлен!\n\nНомер вашего заказа: {order_id}\n\nВ ближайшее время с вами свяжется наш менеджер для уточнения деталей.'
        text_and_data = [btn_back('menu')]
        schema = [1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
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
        'УСЛОВИЯ ДОСТАВКИ:',
        '',
        'После приобретения товара, отправка осуществляется почтой РФ, через Германию (по мере изменений санкционной политики меняются маршруты)',
        '',
        'Сроки доставки рассчитываются индивидуально: зависят от страны отправки и города доставки (для РФ средний срок доставки 2-3 недель)',
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
        'КОНТАКТЫ:',
        '',
        'Для заказа или других вопросов вы можете обращаться по этому номеру/каналу (АЛЕКСЕЙ СКАЖИТЕ СПОСОБ СВЯЗИ)',
       
        sep='\n'
        )
    text_and_data = [
        ['VK', 'https://vk.com/concierge_shopping'],
        ['TG', 'https://t.me/Concierge_Shopping'],
        ['TikTok', 'https://www.tiktok.com/@concierge_shopping?_t=8awO3chvF3Z&_r=1'],
        ['YouTube', 'https://youtube.com/@concierge_shopping'],
        btn_back('menu')
    ]
    schema = [1,1, 1,1, 1]
    button_type = ['url', 'url', 'url', 'url', 'callback_data']
    inline_kb = InlineConstructor.create_kb(text_and_data, schema, button_type)
    return text, inline_kb

def inline_kb_lk(tg_id : str):
    text = markdown.text(
        'ЛИЧНЫЙ КАБИНЕТ\n'
    )

    promocodes = get_promocode(tg_id=tg_id)
    user = get_user(tg_id=tg_id)

    if user.sizes:
        all_sizes = {'1': 'XXS', '2': 'XS', '3': 'S', '4': 'M', '5': 'L', '6': 'XL', '7': '2Xl', '8': '3XL', '9': '4XL'}
        sizes_str = ''
        for s in sorted([int(s) for s in str(user.sizes).split('-')]):
            sizes_str += f"{all_sizes[str(s)]}, "
        sizes_str = sizes_str.strip(', ')
        text += f'\nИзбранные размеры одежды:\n{sizes_str}\n'

    if user.shoe_sizes:
        shoe_sizes_str = ''
        for s in sorted([float(s) for s in str(user.shoe_sizes).split('-')]):
            shoe_sizes_str += f"{str(s).replace('.0', '')}, "
        shoe_sizes_str = shoe_sizes_str.strip(', ')
        text += f'\nИзбранные размеры обуви:\n{shoe_sizes_str}\n'
    
    if user.prices:
        prices_start = {'1': '0', '2': '10000', '3': '20000', '4': '50000 +'}
        prices_end = {'1': '10000', '2': '20000', '3': '50000', '4': '+'}
        
        sizes_list = sorted([int(s) for s in str(user.prices).split('-')])
        print(sizes_list)
        sizes_str = f'{prices_start[str(sizes_list[0])]} - {prices_end[str(sizes_list[-1])]}'
        if str(sizes_list[-1]) == '4':
            sizes_str = sizes_str.replace('- ', '')
        text += f'\nИзбранный диапазон цен:\n{sizes_str} руб.\n'
    if user.brands:
        text += f'\nИзбранные бренды:\n'
        for brand in str(user.brands).split('-'):
            cat = get_category(id=int(brand))
            text += f'{cat.name}, '
        text = text.strip(', ')
        text += '\n'
    if promocodes:
        print(promocodes)
        text += f'\nМои промокоды:'
        for promocode in promocodes:
            text += emojize(f'\n:sparkle:{promocode.name} (', language='alias')
            for pc in get_promocodecategory(promocode_id=promocode.id):
                category = get_category(id=pc.category.id)
                text += f'{category.name} -{pc.discount}%, '
            text = text.strip(', ')
            text += ')'

    text_and_data = [
        [emojize(':money_with_wings: Ввести промокод', language='alias'), 'btn_promocode'],
        [emojize(':shirt: Мои размеры одежды', language='alias'), f'btn_mysizes_'],
        [emojize(':athletic_shoe: Мои размеры обуви', language='alias'), f'btn_mshs_'],
        [emojize(':fleur_de_lis: Мои бренды', language='alias'), f'btn_mybr_'],
        [emojize(':hand_with_index_finger_and_thumb_crossed: Мои цены', language='alias'), 'btn_pr_'],
        btn_back('menu')
    ]
    schema = [1, 1, 1, 1, 1, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_mysizes(sizes : str):
    text = 'Выберите размеры одежды, по которым хотите получать уникальные предложения'
    text_and_data = []
    all_sizes = {'1': 'XXS', '2': 'XS', '3': 'S', '4': 'M', '5': 'L', '6': 'XL', '7': '3Xl', '8': '4XL', '9': '5XL'}
    for id, size in all_sizes.items():
        if len(sizes) > 0:
            if id in sizes:
                sizes_code = ''
                new_sizes = [s for s in sizes.split('-')]
                new_sizes.remove(id)
                for ns in new_sizes:
                    sizes_code += f'{ns}-'
                sizes_code = sizes_code.strip('-')
                text_and_data.append([emojize(f':white_check_mark: {size}', language='alias'), f'btn_mysizes_{sizes_code}'])
            else:
                sizes_code = ''
                new_sizes = [s for s in sizes.split('-')]
                new_sizes.append(id)
                for ns in new_sizes:
                    sizes_code += f'{ns}-'
                sizes_code = sizes_code.strip('-')
                text_and_data.append([emojize(f'{size}', language='alias'), f'btn_mysizes_{sizes_code}'])
        else:
            text_and_data.append([emojize(f'{size}', language='alias'), f'btn_mysizes_{id}'])
    
    schema = [3, 3, 3]
    text_and_data.append(btn_back('lk'))
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_myshoesizes(sizes : list):
    text = 'Выберите размеры обуви, по которым хотите получать уникальные предложения (максимум 10)'
    text_and_data = []
    
    all_sizes = ['35', '35.5', '36', '36.5', '37', '37.5', '38', '38.5', '39', '39.5', '40', '40.5', '41', '41.5', '42', '42.5', '43', '43.5', '44', '44.5', '45', '45.5', '46', '46.5', '47', '47.5', '48', '48.5', '49', '49.5', '50', '50.5', '51', '51.5', '52', '52.5']
    print(sizes)
    for size in all_sizes:
        if len(sizes) > 0:
            if size in sizes:
                sizes_code = ''
                new_sizes = [s for s in sizes]
                new_sizes.remove(size)
                for ns in new_sizes:
                    sizes_code += f'{ns}-'
                sizes_code = sizes_code.strip('-')
                text_and_data.append([emojize(f':white_check_mark: {size}', language='alias'), f'btn_mshs_{sizes_code}'])
            else:
                sizes_code = ''
                new_sizes = [s for s in sizes]
                new_sizes.append(size)
                for ns in new_sizes:
                    sizes_code += f'{ns}-'
                sizes_code = sizes_code.strip('-')
                text_and_data.append([emojize(f'{size}', language='alias'), f'btn_mshs_{sizes_code}'])
        else:
            text_and_data.append([emojize(f'{size}', language='alias'), f'btn_mshs_{size}'])
    schema = [4, 4, 4, 4, 4, 4, 4, 4, 4]
    text_and_data.append(btn_back('lk'))
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_mybrands(brands : list):
    text = 'Выберите бренды, по которым хотите получать уникальные предложения'
    text_and_data = []
    schema = []
    all_brands = [category.id for category in get_category() if category.custom]
    for brand in all_brands:
        if len(brands) > 0:
            if str(brand) in brands:
                brands_code = ''
                new_brands = [s for s in brands]
                new_brands.remove(str(brand))
                for ns in new_brands:
                    brands_code += f'{ns}-'
                brands_code = brands_code.strip('-')
                text_and_data.append([emojize(f':white_check_mark: {get_category(id=brand).name}', language='alias'), f'btn_mybr_{brands_code}'])
            else:
                brands_code = ''
                new_brands = [s for s in brands]
                new_brands.append(str(brand))
                for ns in new_brands:
                    brands_code += f'{ns}-'
                brands_code = brands_code.strip('-')
                text_and_data.append([emojize(f'{get_category(id=brand).name}', language='alias'), f'btn_mybr_{brands_code}'])
        else:
            text_and_data.append([emojize(f'{get_category(id=brand).name}', language='alias'), f'btn_mybr_{brand}'])
    for _ in range(len(all_brands)):
        schema.append(1)
    text_and_data.append(btn_back('lk'))
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb
    
def inline_kb_myprices(prices : str):
    text = 'Выберите диапазоны цен, в рамках которых хотите получать уникальные предложения'
    text_and_data = []
    all_prices = {'1': 'до 10000 руб.', '2': 'от 10000 до 20000 руб.', '3': 'от 20000 до 50000 руб.', '4': 'от 50000 руб.'}
    for id, price in all_prices.items():
        if len(prices) > 0:
            if id in prices:
                prices_code = ''
                new_prices = [s for s in prices.split('-')]
                new_prices.remove(id)
                for ns in new_prices:
                    prices_code += f'{ns}-'
                prices_code = prices_code.strip('-')
                text_and_data.append([emojize(f':white_check_mark: {price}', language='alias'), f'btn_pr_{prices_code}'])
            else:
                prices_code = ''
                new_prices = [s for s in prices.split('-')]
                new_prices.append(id)
                for ns in new_prices:
                    prices_code += f'{ns}-'
                prices_code = prices_code.strip('-')
                text_and_data.append([emojize(f'{price}', language='alias'), f'btn_pr_{prices_code}'])
        else:
            text_and_data.append([emojize(f'{price}', language='alias'), f'btn_pr_{id}'])
    
    schema = [1, 1, 1, 1]
    text_and_data.append(btn_back('lk'))
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_sizes(category_id : int):
    text = 'ТАБЛИЦА РАЗМЕРОВ'
    text_and_data = [['Скрыть', 'btn_hide']]
    schema = [1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_howto():
    text = markdown.text(
        'КАК СДЕЛАТЬ ЗАКАЗ:',
        '',
        '- Вы присылаете скриншот нужного вам товара с характеристикой (размер, если одежда/ обувь и тд)',
        '- Согласовываем с вами цену',
        '- Вы оплачиваете удобным для Вас способом? (USDT/ПЕРЕВОД)',
        '- Мы оформляем доставку (для этого от Вас потребуется ФИО, номер телефона, адрес)',
        '- Вы ожидаете доставку посылки до двери или до отделения почты',
        sep='\n'
        )
    text_and_data = [btn_back('menu')]
    schema = [1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
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
        ['Сообщение пользователям', 'btn_sendmessage'],
        ['WhatsApp каталоги', 'btn_wacatalogs'],
        ['Поиск товара', 'btn_finditem'],
        ['Промокоды', 'btn_promocodes'],
        btn_back('menu')
    ]
    schema = [1, 1, 1, 1, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

def inline_kb_promocodes():
    text = markdown.text(
        'КАБИНЕТ АДМИНИСТРАТОРА',
        'Выберите промокод для редактирования или добавьте новый',
        sep='\n\n'
    )
    text_and_data = []
    schema = []
    promocodes = get_promocode()
    for promocode in promocodes:
        text_and_data.append([f'{promocode.name}', f'btn_editpromocode_{promocode.id}'])
        schema.append(1)

    text_and_data.append(['Добавить промокод', 'btn_addpromocode'])
    schema.append(1)
    text_and_data.append(btn_back('admin'))
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb 

def inline_kb_editpromocode(promocode_id : int):
    promocode = get_promocode(id=promocode_id)
    users = get_promocode(id=promocode_id, users=True)
    promo_categories = ''
    for pc in get_promocodecategory(promocode_id=promocode_id):
        category = get_category(id=pc.category.id)
        promo_categories += f'- {category.name} (- {pc.discount} %)\n'
    text = markdown.text(
        f'Промокод: {promocode.name}\n',
        f'Категории и размеры скидок:\n{promo_categories}',
        f'Промокодом воспользовались {len(users)} человек',
        sep='\n')
    text_and_data = [
        ['Изменить скидку для категории', f'btn_editpd_{promocode.id}'],
        ['Статистика', f'btn_userspromocode_{promocode.id}'],
        ['Удалить промокод', f'btn_removepromocode_{promocode.id}'],
        btn_back('promocodes')
    ]
    schema = [1, 1, 1, 1]
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb 

def inline_kb_editpromocodediscount(promocode_id : int):
    promocode = get_promocode(id=promocode_id)
    text = f'Выберите категорию скидку по которой хотите изменить для промокода {promocode.name}'
    text_and_data = []
    schema = []
    promcats = get_promocodecategory(promocode_id=promocode_id)
    for cat in promcats:
        category = get_category(id=cat.category.id)
        text_and_data.append([category.name, f'btn_editpd_{promocode.id}_{category.id}'])
        schema.append(1)
    text_and_data.append(btn_back('editpromocode'))
    schema.append(1)
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb 


def inline_kb_addpromocode_catalogs(name : str, discount : int, cat_ids : list = []):
    text = markdown.text(
        f'Выберите категории, на который будет распространяться промокод {name}'
    )
    promocode = get_promocode(name=name)
    
    categories = get_category()
    text_and_data = []
    schema = []

    if bool(categories):
        for cat in categories:
            if str(cat.id) in cat_ids:
                cats_code = ''
                new_cats = [cat for cat in cat_ids]
                new_cats.remove(str(cat.id))
                for ncat in new_cats:
                    cats_code += ncat + '-'
                cats_code = cats_code.strip('-')
                new_cats = []
                text_and_data.append([emojize(f':white_check_mark:{cat.name}', language='alias'), f'btn_promocodecategory_{promocode.id}_{cats_code}_{discount}'])
            else:

                cats_code = ''
                new_cats = [cat for cat in cat_ids]
                new_cats.append(str(cat.id))
                for ncat in new_cats:
                    cats_code += ncat + '-'
                cats_code = cats_code.strip('-')
                new_cats = []
                text_and_data.append([f'{cat.name}', f'btn_promocodecategory_{promocode.id}_{cats_code}_{discount}'])
            schema.append(1)
        text_and_data.append([emojize(':heavy_check_mark: Применить', language='alias'), 'btn_promocodes'])
        schema.append(1)
    else:
        text = 'У вас нет доступных категорий, промокод по умолчанию будет распространяться на все'
    inline_kb = InlineConstructor.create_kb(text_and_data, schema)
    return text, inline_kb

# вотсап каталоги
def inline_kb_wacatalogs():
    text = markdown.text(
        'КАБИНЕТ АДМИНИСТРАТОРА'
    )
    text_and_data = [
        ['Добавить каталог', 'btn_addcatalog'],
        ['Удалить каталог', 'btn_delcatalog'],
        ['Редактировать каталог', 'btn_editcatalog'],
        ['Обновление каталогов', 'btn_updatecatalog'],
        btn_back('admin')
    ]
    schema = [1, 1, 1, 1, 1]
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
    text_and_data.append(btn_back('wacatalogs'))
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
    text_and_data.append(btn_back('wacatalogs'))
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
    text_and_data.append(btn_back('wacatalogs'))
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