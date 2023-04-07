from arsenic import get_session, services, browsers, stop_session
from arsenic.constants import SelectorType
import asyncio, aiohttp
import logging

import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup as bs
import time
import sys

from database import crud



#https://web.whatsapp.com/catalog/393421807916
#https://web.whatsapp.com/catalog/390143686270 категории
#https://web.whatsapp.com/catalog/393402619854
#https://web.whatsapp.com/catalog/393459256804 категории
#https://web.whatsapp.com/catalog/393455824868 категории
#https://web.whatsapp.com/catalog/390421309086 категории
#https://web.whatsapp.com/catalog/393459782801
#https://web.whatsapp.com/catalog/393442207025 категории
#https://web.whatsapp.com/catalog/393346770418
#https://web.whatsapp.com/catalog/393423615253 категории
#https://web.whatsapp.com/catalog/390143340192 категории
#https://web.whatsapp.com/catalog/393427688947
#https://wa.me/c/393408371555

#https://wa.me/c/393357824569
#https://wa.me/c/393451792120
#https://wa.me/c/393517727683



def euro_cost():
    webpage = requests.get('https://ligovka.ru/pda/')
    soup = bs(webpage.text, 'html.parser')
    course = soup.find('section', 'main_courses').find_all('div', 'currency_contaner')[1].find_all('tr')[1].find_all('td')[2].text
    return float(course)


# функция парсит товары 
async def get_items(category : str, session, subcategory : str = 'Другое'):
    items = []
    description = None
    price = None
    for i in range(1, 400):
        try:
            img = await session.get_screenshot()
            with open('parser/opened_subcategory.png', 'wb') as png:
                png.write(img.read())

            if subcategory == 'Другое':
                item_xpath = f'//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div[2]/div/div/div/div[{i}]/div/div/div[2]/div/div[1]/span'
            else:
                item_xpath = f'//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div/div/div/div[{i}]/div/div/div[2]/div[1]/div/span'
            
            item_el = await session.wait_for_element(10, item_xpath, SelectorType.xpath)
            
            await item_el.click()

            if subcategory == 'Другое':
                title_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div/div[3]/div[1]/span'
            else:
                title_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[3]/div[1]/span'
            title_el = await session.wait_for_element(10, title_xpath, SelectorType.xpath)
            title = await title_el.get_text()
            #
            logging.info(title)
            time.sleep(1)
            if subcategory == 'Другое':
                img_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div/div[2]/div/div[1]/div[1]/div/img'
                img_el = await session.wait_for_element(10, img_xpath, SelectorType.xpath)
                img = await img_el.get_screenshot()
            else:
                try:
                    img_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[2]/div/div[1]/div/div/img'
                    img_el = await session.wait_for_element(10, img_xpath, SelectorType.xpath)
                    img = await img_el.get_screenshot()
                # сохраняем изображениe
                except:
                    img_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[2]/div/div[1]/div[1]/div/img'
                    img_el = await session.wait_for_element(10, img_xpath, SelectorType.xpath)
                    img = await img_el.get_screenshot()
            #создаем дирректорию категории если ее еще нет
            if not os.path.exists(f"database/images/{category}"):
                os.mkdir(f"database/images/{category}")

            if subcategory == 'Другое':
                with open(f"database/images/{category}/{i}_{title.replace(' ', '_').replace('/', '_')}.png", 'wb') as png:
                    png.write(img.read())
            else:
                if not os.path.exists(f"database/images/{category}/{subcategory}"):
                    os.mkdir(f"database/images/{category}/{subcategory}")
                with open(f"database/images/{category}/{subcategory}/{i}_{title.replace(' ', '_').replace('/', '_')}.png", 'wb') as png:
                    png.write(img.read())
            # записываем данные о товаре
            if subcategory == 'Другое':
                price_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div/div[3]/div[2]/span'
            else:
                price_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[3]/div[2]/span'
            try:
                # получаем цену (если есть)
                
                price_el = await session.get_element(price_xpath, SelectorType.xpath)
                price_text = await price_el.get_text()
                logging.info(price_text)
                price = int(price_text.strip(' €').strip(',00').replace(' ', ''))
                #price = float(browser.find_element(By.XPATH, price_xpath).text.strip(' €').replace(',', '.'))
            except:
                logging.info('no price')

            if subcategory == 'Другое':
                description_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div/div[3]/div[3]'
            else:    
                description_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[3]/div[3]'
            try:
                # получаем описание (если есть)    
                description_el = await session.get_element(description_xpath, SelectorType.xpath)
                description = await description_el.get_text()
                if description == 'ОТПРАВИТЬ СООБЩЕНИЕ КОМПАНИИ':
                    description = None
            except:
                logging.info('no description')
            subcategory_ = None if subcategory == 'Другое' else subcategory
            if subcategory == 'Другое':
                lst = [title, category, subcategory_, description, price, f"database/images/{category}/{i}_{title.replace(' ', '_').replace('/', '_')}.png"]
            else:
                lst = [title, category, subcategory_, description, price, f"database/images/{category}/{subcategory}/{i}_{title.replace(' ', '_').replace('/', '_')}.png"]
            items.append(lst)
            logging.info(lst)
            # закрываем карточку товара кнопкой "назад"
            if subcategory == 'Другое':
                btn_back_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/header/div/div[1]/div/span'
            else:
                btn_back_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/header/div/div[1]/div/span'
            await asyncio.sleep(1)
            btn_catalog_back = await session.wait_for_element(10, btn_back_xpath, SelectorType.xpath)
            await btn_catalog_back.click()
        except Exception as ex:
            logging.error(ex)
            logging.warning('cant find item')
            
            #if subcategory == 'Другое':
            #    btn_back_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/header/div/div[1]/div/span'
            #else:
            #    btn_back_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/header/div/div[1]/div/span'
            #btn_catalog_back = await session.get_element(btn_back_xpath, SelectorType.xpath)
            #await btn_catalog_back.click()
            break
    # закрываем субкатегорию кнопкой "назад"
    #if subcategory == 'Другое':
    #    btn_back_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/header/div/div[1]/div/span'
    #else:
    #    btn_back_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/header/div/div[1]/div/span'
    #    btn_catalog_back = await session.get_element(btn_back_xpath, SelectorType.xpath)
    #    await btn_catalog_back.click()

        await asyncio.sleep(1)
    logging.info('cancel')
    return items

# функция обрабатывает каталог, открывает категории
async def get_catalog(url):
    print(url)
    logging.info(f'start parsing {url}')

    #options = webdriver.ChromeOptions()
    #options.add_argument('--allow-profiles-outside-user-dir')
    #options.add_argument('--enable-profile-shortcut-manager')
    #options.add_argument(r'user-data-dir=parser/User')
    #options.add_argument('--profile-directory=Profile 1')
    #options.headless = True
    #options.add_argument(
    #    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    
    

    service = services.Chromedriver(binary=ChromeDriverManager().install(), log_file=os.devnull)
    browser = browsers.Chrome()
    browser.capabilities = {
        "goog:chromeOptions": {"args": [
            '--user-data-dir=parser/User', 
            '--headless',
            '--private',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--profile-directory=Profile 1',
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        ]}}
        #'log': {'level': 'warn'}}
    
    async with get_session(service, browser) as session:
        await session.get(url)
        # пытаемся найти заголовок каталога, если его нет - делаем скриншот qr-кода 
        try:
            logging.warning('Попытка входа. Ищем название каталога.')
            header_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div[1]/div/div[2]/div[1]/span'
            header_el = await session.wait_for_element(30, header_xpath, SelectorType.xpath)
            header = await header_el.get_text()
            logging.warning(header)
        except:
            logging.warning('Не удается найти на странице название каталога. Проверьте авторизацию.')
            qc_xpath = '//*[@id="app"]/div/div/div[3]/div[1]/div/div/div[2]/div/canvas'
            qc = await session.wait_for_element(120, qc_xpath, SelectorType.xpath)
            img = await qc.get_screenshot()
            with open('parser/screenshot.png', 'wb') as png:
                png.write(img.read())
            # и снова пытаемся найти заголовок (в это время нужно отсканировать qr-код)
            header_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div[1]/div/div[2]/div[1]/span'
            header_el = await session.wait_for_element(120, header_xpath, SelectorType.xpath)
            header = await header_el.get_text() if header_el else 'не нашлось заголовка...'
            logging.warning(header)
            


        # если в каталоге есть категории
        try:
            check_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div[2]/div/div/div/div[1]/div/div[2]/div/div/div/span'
            await session.wait_for_element(10, check_xpath, SelectorType.xpath)
            logging.info('Catalog with categories')  
            try:
                categories = {}      
                for i in range(1, 50):
                    try:
                        category_xpath = f'//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div[2]/div/div/div/div[{i}]/div/div[2]/div/div/div/span'
                        open_category = await session.get_element(category_xpath, SelectorType.xpath)
                        categories[i] = await open_category.get_text()
                    except:
                        continue
                logging.info(categories)
                
                dct = []
                for key, value in categories.items():
                    if value == 'Все товары':
                        break
                    # скрин открытого каталога
                    img = await session.get_screenshot()
                    with open('parser/opened_catalog.png', 'wb') as png:
                        png.write(img.read())

                    opensubcat_xpath = f'//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div[2]/div/div/div/div[{key}]/div/div[3]/a'
                    
                    # открываем содержимое категории
                    button = await session.wait_for_element(10, opensubcat_xpath, SelectorType.xpath)
                    await button.click()
                    await asyncio.sleep(2)

                    logging.info(f'Start parsing {value} subcategory')
                    products = await get_items(category=header, subcategory=value, session=session)
                    print(products)
                    dct += products
                    logging.info(f'Cancel {value} subcategory')
                    await asyncio.sleep(2)
                    
                    btn_back_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/header/div/div[1]/div/span'
                    btn_catalog_back = await session.wait_for_element(10, btn_back_xpath, SelectorType.xpath)
                    await btn_catalog_back.click()
                    await asyncio.sleep(2)
                    
                return dct
            except Exception as ex:
                logging.error(ex)
                logging.warning(f'Произошла ошибка во время парсинга субкатегории {value}')
                return 1
        # если категорий нет
        except Exception as ex:
            logging.info('Catalog without categories')
            items = await get_items(category=header, session=session)
            return items
    '''
    except Exception as ex:
        print('Парсинг завершен с результатом: 0')
        print(ex)
        return 0
    
    finally:
        browser.quit()
    '''
    
async def get_valentino_catalog(url, subcategory):
    service = services.Chromedriver(binary=ChromeDriverManager().install(), log_file=os.devnull)
    browser = browsers.Chrome()
    browser.capabilities = {
        "goog:chromeOptions": {"args": [
        '--no-sandbox',
            '--user-data-dir=parser/User', 
            '--headless',
            'window-size=1280,720',
            #'--start-maximized',
            
            '--private',
            '--disable-gpu',
            #'--disable-dev-shm-usage',
            '--profile-directory=Profile 1',
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            '--lang="ru"'
        ]}}
    items = []
    async with get_session(service, browser) as session:
        await session.get(url)
        await asyncio.sleep(2)
        num_xpath = '//*[@id="main"]/div/div[1]/div/div[1]/div/div'
        num_el = await session.wait_for_element(10, num_xpath, SelectorType.xpath)
        num_text = await num_el.get_text()
        num = int(num_text.split(' ')[0])

        name_xpath = '//*[@id="main-wrapper"]/div[1]/div[2]'
        name_el = await session.wait_for_element(10, name_xpath, SelectorType.xpath)
        name = await name_el.get_text()
        
        
        try:
            cookie_xpath = f'//*[@id="main-wrapper"]/div[4]/div[2]'
            cookie_el = await session.get_element(cookie_xpath, SelectorType.xpath)
            await cookie_el.click()
        except:
            pass
        
        logging.info(f'Start {subcategory} subcategory')
        
        for i in range(1, 5):# num + 1):
            logging.info(f'{i} {subcategory}')
            item_xpath = f'//*[@id="main"]/div/div[2]/div[1]/div[{i}]/div[2]/div[1]'
            #item_xpath = f'//*[@id="main"]/div/div[2]/div[1]/div[1]/div[2]/div[1]'
            item_el = await session.wait_for_element(10, item_xpath, SelectorType.xpath)
            await item_el.click()
            await asyncio.sleep(1)

            webpage = await session.get_page_source()
            soup = bs(webpage, 'lxml')
            
            name_el = await session.wait_for_element(10, name_xpath, SelectorType.xpath)
            name = await name_el.get_text()
            logging.info('name: ' + name)

            if not os.path.exists(f"database/images/VALENTINO"):
                os.mkdir(f"database/images/VALENTINO")

            if not os.path.exists(f"database/images/VALENTINO/{subcategory}"):
                os.mkdir(f"database/images/VALENTINO/{subcategory}")
            await asyncio.sleep(1)
            images = ''
            for num in range(1, 20):
                try:
                    tag_id = webpage.split('swiper-wrapper-')[-1].split('"')[0]

                    image_xpath = f'//*[@id="swiper-wrapper-{tag_id}"]/div[{num}]/div/div/div/div'                    
                    image_el = await session.get_element(image_xpath, SelectorType.xpath)
                    image_link = await image_el.get_css_value('background-image')
                    #logging.info(image_link.strip('url(').strip(')'))
                    img_path = f"database/images/VALENTINO/{subcategory}/{i}_{name.replace(' ', '_').replace('/', '_')}_{num}.png"
                    request = requests.get(image_link.strip('url("').strip('")'))
                    with open(img_path, 'wb') as png:
                        png.write(request.content)
                    images += img_path + '\n'
                except:
                    pass
            
            price = None
            try:
                price = int(soup.find('p', 'sc-dQDPHY gwUuKq').text.replace('.00', '').strip('€').replace(',', ''))
            except:
                try:
                    try:
                        price = int(soup.find_all('p', 'sc-dQDPHY gwUuKq')[1].text.replace('.00', '').strip('€').replace(',', ''))
                    except:
                        price = int(soup.find_all('div', 'sc-dQDPHY gwUuKq')[0].text.replace('.00', '').strip('€').replace(',', ''))
                except IndexError:
                    pass
                
            #print(f'Цена: {price}')
            
            description = ''
           
            try:
                description = soup.find('div', 'sc-bOSxlg eTpxmk').text
            except:
                pass
            #print(description)

            #sizes_el = await session.get_element('//*[@id="main"]/div/div[2]/div[3]/div[2]/div', SelectorType.xpath)
            #sizes_soup = await sizes_el.get_page_source()
            #print(sizes_soup)
            try:
                description += '\n\nРазмеры:\n'
                sizes = soup.find('div', 'sc-GJyyB kXYhul').find_all('p')
                for size in sizes:
                    if size.get('class')[1] == 'kAJdQY':
                        description += f'<b>{size.text}</b> '
                    elif size.text == 'One Size':
                        description += size.text
                    else:
                        description += f'<s>{size.text}</s> '
            except:
                description += 'One Size'
            
            try:
                name = soup.find('p', 'sc-ialjHA dOuBpq').text
            except:
                try:
                    name = soup.find_all('p', 'sc-ialjHA dOuBpq')[0].text
                except:
                    pass
                

            back_xpath = '//*[@id="main-wrapper"]/div[1]/div[1]'
            back_el = await session.wait_for_element(10, back_xpath, SelectorType.xpath)
            await back_el.click()

            item = [name, 'VALENTINO', subcategory, 'valentino', description, price, images]
            items.append(item)
            logging.info(item)
    return items

async def get_valentino():
    url = 'https://myv-experience.valentino.com/0040001024/OUTLET%20SERRAVALLE'
    categories = [
        '/VAL/search?category=APPAREL',
        '/VAL/search?category=SHOES',
        '/VAL/search?category=BAGS',
        '/VAL/search?category=SMALL%20LEATHER%20GOODS',
        '/VAL/search?category=BIJOUX',
        '/VAL/search?category=SOFT%20ACCESSORIES',
        '/VMA/search?category=APPAREL',
        '/VMA/search?category=SHOES',
        '/VMA/search?category=BAGS',
        '/VMA/search?category=SMALL%20LEATHER%20GOODS',
        '/VMA/search?category=BIJOUX',
        '/VMA/search?category=SOFT%20ACCESSORIES'
    ]
    
    for category_url in categories:
        if 'VMA' in category_url:
            subcategory = 'Man ' + category_url.split('=')[1].replace('%20', ' ')
        else:
            subcategory = 'Woman ' + category_url.split('=')[1].replace('%20', ' ')

        if not crud.subcategory_exists(subcategory):
            crud.create_subcategory(name=subcategory, category='VALENTINO')
        items = []
        items = await get_valentino_catalog(url + category_url, subcategory)
        crud.del_products(subcategory=items[0][2])
        for item in items:
            price = int((item[5] * (euro_cost() + 1)) / 100 * crud.get_catalog(phone='valentino').margin) if item[5] else None
            crud.create_product(
                name=item[0],
                category=item[1],
                subcategory=item[2],
                catalog=item[3],
                description=item[4],
                price=price,
                image=item[6])
    return items


async def get_subcategory(session, url):
  
    urls = []
    for i in range(1, 10):
        urls.append(f'{url}?p={i}')
    items = []
    for url in urls:
        async with session.get(url, ssl=False) as response:
            try:
                resp = await response.text()
                #resp = requests.get(url)
                soup = bs(resp, 'lxml')
                #item = soup.find('div', {'id': 'category-product-list'}).find_all('a', 'MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineAlways css-1mhuhvl')
                for item in [i.find('a').get('href') for i in soup.find('div', {'id': 'category-product-list'}).find_all('div', 'css-rqa33b e198isat2')]:
                    items.append(item)
            except:
                break
    return items

async def get_item(session, url, subcategory, i):
    item = []
    async with session.get(url, ssl=False) as response:
            resp = await response.text()
    #resp = requests.get(url)
    soup = bs(resp, 'lxml')

    name = soup.find('h2', 'MuiTypography-root MuiTypography-h1 e18vcbt23 css-c60yiy').text
    logging.info(f'Start: {name}')
    try:
        description = soup.find('div', 'MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-8 Grid-description e14xbgjz2 css-f1obvg').find('p').text
    except:    
        description = soup.find('div', 'MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-8 Grid-description e14xbgjz2 css-f1obvg').find('div', 'RichContent-Html-Root Magento-PageBuilder-Html MuiBox-root css-ykpcgv').text
  
    try:
        price = float(soup.find('span', 'price css-g6gm48 e15t2uci1').text.strip('€ '))
    except:
        price = float(soup.find('span', 'special-price css-mzijty e15t2uci4').text.strip('€ '))
        
    
    discont = soup.find('div', 'e18vcbt26 css-h9r4rd e15t2uci0').text
    description += f'\n\n{discont}'

    try:
        block_heel = soup.find('div', 'MuiGrid-root e18vcbt20 css-yp95h9').find('h3').text
        description += f'\n\n{block_heel}'
    except:
        pass

    try:
        sizes = '\n\nРазмеры:\n'
        buttons = soup.find('div', 'MuiToggleButtonGroup-root ProductOptions text e18jvxhl2 css-rxylov').find_all('button')
        for button in buttons:
            if 'out-of-stock' in button.get('class'):
                size = f"<s>{button.find('p').text}</s> "
            else:
                size = f"<b>{button.find('p').text}</b> "
            sizes +=size
        description += sizes
    except:
        pass

    if not os.path.exists(f"database/images/LESILLA"):
        os.mkdir(f"database/images/LESILLA")

    if not os.path.exists(f"database/images/LESILLA/{subcategory}"):
        os.mkdir(f"database/images/LESILLA/{subcategory}")

    photo_span = soup.find('div', {'class' : 'Gallery-root'}).find_all('span')
    photo = [img.find('img').attrs['style'].split('background-image:url("')[1].strip('")').replace('q_1,w_30', 'q_100,w_3840') for img in photo_span]
    images = ''
    for url in photo:
        num = photo.index(url) + 1
        img_path = f"database/images/LESILLA/{subcategory}/{i}_{name.replace(' ', '_').replace('/', '_')}_{num}.png"
        request = requests.get(url)
        with open(img_path, 'wb') as png:
            png.write(request.content)
        images += img_path + '\n'
    
    return [name, 'LeSILLA', subcategory, description, price, images]


async def get_lesilla():
    urls = {
        'Туфли на высоком каблуке': 'https://outlet.lesilla.com/row/pumps/high-heels.html',
        'Туфли на среднем каблуке': 'https://outlet.lesilla.com/row/pumps/mid-heels.html',
        'Туфли на плоской подошве': 'https://outlet.lesilla.com/row/pumps/flat.html',
        'Сандалии на высоком каблуке': 'https://outlet.lesilla.com/row/sandals/high-heels.html',
        'Сандалии на среднем каблуке': 'https://outlet.lesilla.com/row/sandals/mid-heels.html',
        'Сандалии на пизкой подошве': 'https://outlet.lesilla.com/row/sandals/flat.html',
        'Танкетки': 'https://outlet.lesilla.com/row/sandals/wedges.html',
        'Обувь на платформе': 'https://outlet.lesilla.com/row/sandals/platform.html',
        'Тапочки сандалии': 'https://outlet.lesilla.com/row/sandals/slippers.html',
        'Высокие кросовки': 'https://outlet.lesilla.com/row/sneaker/high-top.html',
        'Низкие кросовки': 'https://outlet.lesilla.com/row/sneaker/low-top.html',
        'Ботильоны на высоком каблуке': 'https://outlet.lesilla.com/row/ankle-boots/high-heels.html',
        'Ботильоны на среднем каблуке': 'https://outlet.lesilla.com/row/ankle-boots/flat.html',
        'Ботильоны техасцы': 'https://outlet.lesilla.com/row/ankle-boots/texans.html',
        'Сапоги на высоком каблуке': 'https://outlet.lesilla.com/row/boots/high-heels.html',
        'Сапоги на среднем каблуке': 'https://outlet.lesilla.com/row/boots/low-heels.html',
        'Сапоги на плоской подошве': 'https://outlet.lesilla.com/row/flat/ankle-boots.html',
        'Балетки': 'https://outlet.lesilla.com/row/flat/ballets.html',
        'Тапочки на плоскойподошве': 'https://outlet.lesilla.com/row/flat/slippers.html',
        'Мокасины': 'https://outlet.lesilla.com/row/flat/mocassins.html',
        'Сандалии на плоской подошве': 'https://outlet.lesilla.com/row/flat/sandals.html',
        'Сумки': 'https://outlet.lesilla.com/row/bags.html'
    }
    items = []
    async with aiohttp.ClientSession(trust_env=True) as session:
        for name, url in urls.items():
            product_urls = await get_subcategory(session, url)
            for prodict_url in product_urls:
                i = product_urls.index(prodict_url) + 1
                try:
                    items.append(await get_item(session, prodict_url, name, i))
                except:
                    pass
        logging.info(items)
        return items
    