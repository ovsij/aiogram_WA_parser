from arsenic import get_session, services, browsers, stop_session
from arsenic.constants import SelectorType
import asyncio, aiohttp, aiofiles
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
import re
import requests
from bs4 import BeautifulSoup as bs
import time
import sys
import urllib.request

from database.db import *

from database import crud
from bot.loader import dp, bot

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
    try:
        webpage = requests.get('https://www.push52.ru')
        soup = bs(webpage.text, 'html.parser')
        course = soup.find('div', {'id' : 'body_CurrencyBoard1_eurrub'}).find('span', 'sell').text.replace(',', '.')
        return float(course)
    except:
        try:
            webpage = requests.get('https://www.push52.ru')
            soup = bs(webpage.text, 'html.parser')
            course = soup.find_all('div', 'currency_contaner')[1].find_all('tr')[0].find_all('td')[2].text
            return float(course)
        except:
            print('pass')


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
            #logging.info(title)
            time.sleep(1)

            """
            img = await session.get_screenshot()
            with open('item.png', 'wb') as png:
                png.write(img.read())
            if subcategory == 'Другое':
                img_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div/div[2]/div/div[1]/div[1]/div/img'
            else:
                img_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[2]/div/div[1]/div[1]/div/img'
            images_el = await session.wait_for_element(10, img_xpath, SelectorType.xpath)
            print(images_el)
            src = await images_el.get_attribute('src')
            print(src)
           
            
            
            # сохраняем изображения
            webpage = await session.get_page_source()
            soup = bs(webpage, 'lxml')
            image_links = soup.find_all('div', '_1Z_Af')
            for im in image_links:
                print(im.find('img').get('src'))
            
            images = ''
            async with aiohttp.ClientSession() as session:
                for link in image_links:
                    i = image_links.index(link) + 1
                    response = await session.get(url=link.find('img').get('src'), ssl=False)
                    if subcategory == 'Другое':
                        with open(f"database/images/{category}/{i}_{title.replace(' ', '_').replace('/', '_')}.png", 'wb') as png:
                            png.write(response.content)
                        images += f"database/images/{category}/{i}_{title.replace(' ', '_').replace('/', '_')}.png\n"
                    else:
                        if not os.path.exists(f"database/images/{category}/{subcategory}"):
                            os.mkdir(f"database/images/{category}/{subcategory}")
                        with open(f"database/images/{category}/{subcategory}/{i}_{title.replace(' ', '_').replace('/', '_')}.png", 'wb') as png:
                            png.write(response.content)
                        images += f"database/images/{category}/{subcategory}/{i}_{title.replace(' ', '_').replace('/', '_')}.png\n"

            """
            webpage = await session.get_page_source()
            soup = bs(webpage, 'html.parser')
            num_images = len(soup.find_all('div', '_1Z_Af'))
            if num_images > 10:
                num_images = 10
            images = ''
            for im in range(1, num_images + 1):
                
                if subcategory == 'Другое':
                    img_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div/div[2]/div/div[1]/div[1]/div'
                    img_el = await session.wait_for_element(10, img_xpath, SelectorType.xpath)
                    img = await img_el.get_screenshot()
                else:
                    try:
                        img_xpath = f'//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[2]/div/div[1]/div[{im}]/div'
                        img_el = await session.wait_for_element(10, img_xpath, SelectorType.xpath)
                        img = await img_el.get_screenshot()
                        #print('first xpath')
                    except:
                        img_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[2]/div/div[1]/div/div'
                        img_el = await session.wait_for_element(10, img_xpath, SelectorType.xpath)
                        img = await img_el.get_screenshot()
                        #print('second xpath')
        
                #создаем дирректорию категории если ее еще нет
                if not os.path.exists(f"database/images/{category}"):
                    os.mkdir(f"database/images/{category}")

                if subcategory == 'Другое':
                    with open(f"database/images/{category}/{i}_{title.replace(' ', '_').replace('/', '_')}_{im}.png", 'wb') as png:
                        png.write(img.read())
                    images += f"database/images/{category}/{i}_{title.replace(' ', '_').replace('/', '_')}_{im}.png\n"
                else:
                    if not os.path.exists(f"database/images/{category}/{subcategory}"):
                        os.mkdir(f"database/images/{category}/{subcategory}")
                    with open(f"database/images/{category}/{subcategory}/{i}_{title.replace(' ', '_').replace('/', '_')}_{im}.png", 'wb') as png:
                        png.write(img.read())
                    #print(f"database/images/{category}/{subcategory}/{i}_{title.replace(' ', '_').replace('/', '_')}_{im}.png\n")
                    images += f"database/images/{category}/{subcategory}/{i}_{title.replace(' ', '_').replace('/', '_')}_{im}.png\n"
                try:
                    # переключаем на следующее изображение
                    nextimage_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[2]/div/div[3]/span'
                    nextimageimg_el = await session.wait_for_element(2, nextimage_xpath, SelectorType.xpath)
                    await nextimageimg_el.click()
                    await asyncio.sleep(1)
                except:
                    #print('no more images')
                    break
                
        
    
            # записываем данные о товаре
            if subcategory == 'Другое':
                price_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div/div[3]/div[2]/span'
            else:
                price_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[3]/div[2]/span'
            try:
                # получаем цену (если есть)
                
                price_el = await session.get_element(price_xpath, SelectorType.xpath)
                price_text = await price_el.get_text()
                price = int(price_text.strip(' €').replace(',00', '').replace(' ', ''))
                #price = float(browser.find_element(By.XPATH, price_xpath).text.strip(' €').replace(',', '.'))
            except:
                #logging.info('no price')
                pass

            if subcategory == 'Другое':
                description_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div/div[3]/div[3]'
            else:    
                description_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/span/div/div[2]/div/div[3]/div[3]'
            try:
                # получаем описание (если есть)    
                description_el = await session.get_element(description_xpath, SelectorType.xpath)
                description = await description_el.get_text()
                if description == 'ОТПРАВИТЬ СООБЩЕНИЕ КОМПАНИИ' and category != 'FURLA DESIGNER OUTLET SERRAVALLE':
                    description = None
            except:
                #logging.info('no description')
                pass

            if category == 'FURLA DESIGNER OUTLET SERRAVALLE':
                description = soup.find('div', 'f8jlpxt4 e4qy2s3t e1gr2w1z du8bjn1j gfz4du6o r7fjleex b6f1x6w7').find('span').text
                for i in re.findall(r'€.?\d*', description):
                    description = description.replace(i, str(int((int(i.strip('€').strip(' ')) * (euro_cost() + 1)) * float(f'1.{crud.get_category(phone="390143686270").margin}'))) + ' руб.')
            img = await session.get_screenshot()
            with open('parser/check.png', 'wb') as png:
                png.write(img.read())
            

            subcategory_ = None if subcategory == 'Другое' else subcategory
            if subcategory == 'Другое':
                lst = [title, category, subcategory_, description, price, images]
            else:
                lst = [title, category, subcategory_, description, price, images]
            #print(lst)
            items.append(lst)
            #logging.info(lst)
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
    #logging.info('cancel')
    return items

# функция обрабатывает каталог, открывает категории
async def get_catalog(url):
    #print(url)
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
            'window-size=1920, 1080',
            #'--start-maximized',
            '--private',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--profile-directory=Profile 1',
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        ]}}
        #'log': {'level': 'warn'}}
    
    async with get_session(service, browser) as session:
        await session.get(url)#'https://web.whatsapp.com')
        #await session.set_window_fullscreen()
        # пытаемся найти заголовок каталога, если его нет - делаем скриншот qr-кода 
        try:
            logging.warning('Попытка входа. Ищем название каталога.')
            header_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div[1]/div/div[2]/div[1]/span'
            header_el = await session.wait_for_element(30, header_xpath, SelectorType.xpath)
            header = await header_el.get_text()
            logging.warning(header)
        except:
            try:
                logging.warning('Не удается найти на странице название каталога. Проверьте авторизацию.')
                qc_xpath = '//*[@id="app"]/div/div/div[3]/div[1]/div/div/div[2]/div/canvas'
                img = await session.get_screenshot()
                with open('parser/checklogin.png', 'wb') as png:
                    png.write(img.read())
                #qc = await session.wait_for_element_gone(120, qc_xpath, SelectorType.xpath)
                #print(qc)
                await asyncio.sleep(20)
                #qc = None
                
                img1 = await session.get_screenshot()

                with open('parser/screenshot.png', 'wb') as png:
                    png.write(img1.read())
                # и снова пытаемся найти заголовок (в это время нужно отсканировать qr-код)
                header_xpath = '//*[@id="app"]/div/div/div[6]/span/div/span/div/div[2]/div[1]/div/div[2]/div[1]/span'
                header_el = await session.wait_for_element(120, header_xpath, SelectorType.xpath)
                header = await header_el.get_text() if header_el else 'не нашлось заголовка...'
            except Exception as ex:
                print(ex)
            
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
                    #if value == 'Все товары':
                    #    break
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
                    #print(products)
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
        #'window-size=1280,720',
        '--start-maximized',
        
        '--private',
        '--disable-gpu',
        '--disable-dev-shm-usage',
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
            cookie_xpath = f'//*[@id="onetrust-accept-btn-handler"]'
            cookie_el = await session.get_element(cookie_xpath, SelectorType.xpath)
            await cookie_el.click()
        except:
            pass
        
        logging.info(f'Start VALENTINO {subcategory} subcategory')
        euro_costs = euro_cost()
        for i in range(1, 5):# num + 1):
            try:
                #logging.info(f'{i} {subcategory}')
                item_xpath = f'//*[@id="main"]/div/div[2]/div[1]/div[{i}]/div[2]/div[1]'
                #item_xpath = f'//*[@id="main"]/div/div[2]/div[1]/div[1]/div[2]/div[1]'
                item_el = await session.wait_for_element(10, item_xpath, SelectorType.xpath)
                await item_el.click()
                await asyncio.sleep(1)

                webpage = await session.get_page_source()
                soup = bs(webpage, 'lxml')

                url = await session.get_url()

                name_el = await session.wait_for_element(10, name_xpath, SelectorType.xpath)
                name = await name_el.get_text()
                article = name
                logging.info('name: ' + name)

                if not os.path.exists(f"database/images/VALENTINO"):
                    os.mkdir(f"database/images/VALENTINO")

                if not os.path.exists(f"database/images/VALENTINO/{subcategory}"):
                    os.mkdir(f"database/images/VALENTINO/{subcategory}")
                await asyncio.sleep(1)
                images = ''
                for num in range(1, 11):
                    try:
                        tag_id = webpage.split('swiper-wrapper-')[-1].split('"')[0]

                        image_xpath = f'//*[@id="swiper-wrapper-{tag_id}"]/div[{num}]/div/div/div/div'                    
                        image_el = await session.get_element(image_xpath, SelectorType.xpath)
                        image_link = await image_el.get_css_value('background-image')
                        #logging.info(image_link.strip('url(').strip(')'))
                        img_path = f"database/images/VALENTINO/{subcategory}/{i}_{name.replace(' ', '_').replace('/', '_')}_{num}.png"
                        images += img_path + '\n'
                        if os.path.exists(img_path):
                            continue
                        if not os.path.exists(img_path):
                            request = requests.get(image_link.strip('url("').strip('")'))
                            with open(img_path, 'wb') as png:
                                png.write(request.content)
                        
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
                    except:
                        await session.set_window_fullscreen()
                        img1 = await session.get_screenshot()

                        with open('parser/screenshot.png', 'wb') as png:
                            png.write(img1.read())
                        price_xpath = '//*[@id="main"]/div/div/div[1]/div[1]/p'                    
                        price_el = await session.get_element(price_xpath, SelectorType.xpath)
                        price = await price_el.get_text()
                        print(price)
                
                price = int((price * (euro_costs + 1)) * float(f'1.{crud.get_category(name="VALENTINO").margin}')) if price else None
                print(f'Цена: {price}')
                
                description = ''
            
                #try:
                    #description = soup.find('div', 'sc-bOSxlg eTpxmk').text
                #except:
                #    pass
                #print(description)

                #sizes_el = await session.get_element('//*[@id="main"]/div/div[2]/div[3]/div[2]/div', SelectorType.xpath)
                #sizes_soup = await sizes_el.get_page_source()
                #print(sizes_soup)
                try:
                    list_sizes = ''
                    description += '\n\nРазмеры:\n'
                    sizes = soup.find('div', 'sc-GJyyB kXYhul').find_all('p')
                    for size in sizes:
                        if size.get('class')[-1] == 'kAJdQY':
                            description += f'<b>{size.text.strip("/")}</b> '
                            list_sizes += size.text.strip('/') + ', '
                        elif size.text == 'One Size':
                            description += size.text
                        else:
                            description += f'<s>{size.text.strip("/")}</s> '
                    list_sizes = list_sizes[:-2]
                except:
                    description += 'One Size'
                
                try:
                    name = soup.find('p', 'sc-ialjHA dOuBpq').text
                except:
                    try:
                        name = soup.find_all('p', 'sc-ialjHA dOuBpq')[0].text
                    except:
                        pass
                print(name)
                
                back_xpath = '//*[@id="main-wrapper"]/div[1]/div[1]'
                back_el = await session.wait_for_element(10, back_xpath, SelectorType.xpath)
                await back_el.click()
                print(price)
                if price:
                    item = [name, 'VALENTINO', subcategory, 'valentino', description, price, images, list_sizes, article, url]
                    items.append(item)
                #logging.info(item)
                #print(item)
            except Exception as ex:
                print(ex)
        
    return items

async def get_valentino():
    
    url = 'https://myv-experience.valentino.com/0040001024/OUTLET%20SERRAVALLE'
    subcategories = [
        ['Женщины'],
        ['Женская одежда', 'Женщины', 2, '/VAL/search?category=APPAREL'],
        ['Женская обувь', 'Женщины', 2, '/VAL/search?category=SHOES'],
        ['Женские сумки', 'Женщины', 2, '/VAL/search?category=BAGS'],
        ['Женские кожаные изделия', 'Женщины', 2, '/VAL/search?category=SMALL%20LEATHER%20GOODS'],
        ['Женская бижутерия', 'Женщины', 2, '/VAL/search?category=BIJOUX'],
        ['Женские аксессуары', 'Женщины', 2, '/VAL/search?category=SOFT%20ACCESSORIES'],
        ['Мужчины'],
        ['Мужская одежда', 'Мужчины', 2, '/VMA/search?category=APPAREL'],
        ['Мужская обувь', 'Мужчины', 2, '/VMA/search?category=SHOES'],
        ['Мужские сумки', 'Мужчины', 2, '/VMA/search?category=BAGS'],
        ['Мужские кожаные изделия', 'Мужчины', 2, '/VMA/search?category=SMALL%20LEATHER%20GOODS'],
        ['Мужская бижутерия', 'Мужчины', 2, '/VMA/search?category=BIJOUX'],
        ['Мужские аксессуары', 'Мужчины', 2, '/VMA/search?category=SOFT%20ACCESSORIES']
    ]
    cat_name = 'VALENTINO'
    for subcategory in subcategories:
        if len(subcategory) == 1:
            s = crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            continue
        elif not isinstance(subcategory[-1], str):
            if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
                crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue

        logging.info(f'Start VALENTINO {subcategory}')
        
        items = await get_valentino_catalog(url + subcategory[-1], subcategory[0])
        print(items)
        #crud.del_products(subcategory=subcategory, category='VALENTINO')
        #print(crud.get_product(category_id=crud.get_category(name='VALENTINO').id, subcategory_id=1))
        #try:
        #    not_deleted_items = [product.name for product in crud.get_product(category_id=crud.get_category(name='VALENTINO').id, subcategory_id=crud.get_subcategory(name=subcategory).id)]
        #except:
        #    not_deleted_items = []
        #print(not_deleted_items)
        
            
        if not crud.subcategory_exists(name=subcategory[0], category='VALENTINO'):
            metacategory = crud.get_metacategory(name='Premium бренды')
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name='VALENTINO', metacategory=metacategory.id).id)
            crud.create_subcategory(name=subcategory[0], category='VALENTINO', parent_subcategory=parent_subcategory.id, level=subcategory[2])
        
        crud.create_products(category='VALENTINO', subcategory=subcategory[0], items=items)
            
        logging.info(f'Canceled VALENTINO {subcategory[0]} added {len(items)} products') 
    await bot.send_message(227184505, f'VALENTINO закончил парсинг')
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

# lesilla
async def get_item(session, url, subcategory, i):
    
    article = url.split('.')[-2].split('-')[-1]
    item = []
    async with session.get(url, ssl=False) as response:
        resp = await response.text()
    #resp = requests.get(url)
    soup = bs(resp, 'lxml')

    name = soup.find('h2', 'MuiTypography-root MuiTypography-h1 e18vcbt23 css-c60yiy').text
    #logging.info(f'Start: {name}')
    description = ''
    #try:
    #    description = soup.find('div', 'MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-8 Grid-description e14xbgjz2 css-f1obvg').find('p').text
    #except:    
    #    description = soup.find('div', 'MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-8 Grid-description e14xbgjz2 css-f1obvg').find('div', 'RichContent-Html-Root Magento-PageBuilder-Html MuiBox-root css-ykpcgv').text
  
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
        list_sizes = ''
        sizes = '\n\nРазмеры:\n'
        buttons = soup.find('div', 'MuiToggleButtonGroup-root ProductOptions text e18jvxhl2 css-rxylov').find_all('button')
        for button in buttons:
            if 'out-of-stock' in button.get('class'):
                size = f"<s>{button.find('p').text}</s> "
            else:
                list_sizes += button.find('p').text + ', '
                size = f"<b>{button.find('p').text}</b> "
            sizes +=size
        description += sizes
        list_sizes = list_sizes[:-2]
    except:
        pass
    try:
        color = soup.find('h1', 'MuiTypography-root MuiTypography-body1 e18vcbt24 css-1u83stg').text
    except:
        color = 0
    if not os.path.exists(f"database/images/LESILLA"):
        os.mkdir(f"database/images/LESILLA")

    if not os.path.exists(f"database/images/LESILLA/{subcategory}"):
        os.mkdir(f"database/images/LESILLA/{subcategory}")

    photo_span = soup.find('div', {'class' : 'Gallery-root'}).find_all('span')
    photo = [img.find('img').attrs['style'].split('background-image:url("')[1].strip('")').replace('q_1,w_30', 'q_100,w_3840') for img in photo_span]
    images = ''
    for url in photo[:10]:
        num = photo.index(url) + 1
        img_path = f"database/images/LESILLA/{subcategory}/{i}_{name.replace(' ', '_').replace('/', '_')}_{num}.png"
        images += img_path + '\n'
        if os.path.exists(img_path):
            continue
        request = requests.get(url)
        with open(img_path, 'wb') as png:
            png.write(request.content)
            
    return [name, 'LeSILLA', subcategory, 'lesilla', description, price, images, color, list_sizes, article, url]


async def get_lesilla():
    urls = {
        'Туфли на высоком каблуке': 'https://outlet.lesilla.com/row/pumps/high-heels.html',
        'Туфли на среднем каблуке': 'https://outlet.lesilla.com/row/pumps/mid-heels.html',
        'Туфли на плоской подошве': 'https://outlet.lesilla.com/row/pumps/flat.html',
        'Сандалии на высоком каблуке': 'https://outlet.lesilla.com/row/sandals/high-heels.html',
        'Сандалии на среднем каблуке': 'https://outlet.lesilla.com/row/sandals/mid-heels.html',
        'Сандалии на низкой подошве': 'https://outlet.lesilla.com/row/sandals/flat.html',
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
    
    async with aiohttp.ClientSession(trust_env=True) as session:
        for name, url in urls.items():
            logging.info(f'Starting LeSILLA: {name}')
            product_urls = await get_subcategory(session, url)
            items = []
            for prodict_url in product_urls:
                i = product_urls.index(prodict_url) + 1
                try:
                    await asyncio.sleep(2)
                    items.append(await get_item(session, prodict_url, name, i))
                except:
                    continue
            #crud.del_products(subcategory=name, category='LeSILLA')
            #try:
            #    not_deleted_items = [product.name + product.description.split('Color:')[1].split('\n\n')[0] for product in crud.get_product(category_id=crud.get_category(name='LeSILLA').id, subcategory_id=crud.get_subcategory(name=name).id)]
            #except:
            #    not_deleted_items = []
            #print(not_deleted_items)
            euro_costs = euro_cost()
            for item in items:
                try:
                    price = int((item[5] * (euro_costs + 1)) * float(f'1.{crud.get_category(name="LeSILLA Outlet").margin}')) if item[5] else None
                    description = item[4].replace('€ ', ' ')
                    for i in re.findall(r'\d*[.]\d\d', item[4]):
                        if i:
                            price_rub = str(int((float(i) * (euro_costs + 1)) / 100 * crud.get_category(name='LeSILLA Outlet').margin))
                            description = description.replace(i, '<s>' + price_rub + ' руб.</s>  ')
                    description = f'Color: {item[7]}\n\n' + description.replace(f'<s>{price_rub} руб.</s>', f'{price_rub} руб.')
                    #if item[0] + ' ' + item[7] in not_deleted_items:
                    #    continue
                    if not crud.product_exists(article=item[9]):
                        prod = crud.create_product(
                        name=item[0],
                        category='LeSILLA Outlet',
                        subcategory=name,
                        description=description,
                        sizes=item[7],
                        price=price,
                        image=item[6],
                        article=item[9],
                        url=item[10])
                    else:
                        prod = crud.get_product(article=item[9])
                        if not prod.deleted and not prod.edited:
                            crud.update_product(
                                product_id=prod.id,
                                name=item[0],
                                category='LeSILLA Outlet',
                                description=description,
                                sizes=item[7],
                                price=price,
                                image=item[6],
                                article=item[9],
                                url=item[10]
                            )
                except Exception as ex:
                    logging.warning(f'LeSILLA db - {ex}')
                
            logging.info(f'Canceled LeSILLA {name} added {len(items)} products')
        await bot.send_message(227184505, f'LeSILLA закончил парсинг')
        return items


def image_func(image):
    try:
        image = image['properties']["portraitURL"].replace('t_default', 't_PDP_1280_v1/f_auto,q_auto:eco')
        return image
    except:
        return 0

async def get_nike_subcategory(session, url, subcategory, category):
    if subcategory == 'Детские аскессуары':
        async with session.get('https://www.nike.com/it/w/bambini-outlet-accessori-3yaepzawwpwzv4dh', ssl=False) as response:
            webpage = await response.text()
            soup = bs(webpage, 'html.parser')
            items = [item.find('figure').find('a').get('href') for item in soup.find_all('div', 'product-card__body')]
            products = []
            for item in items:
                dct = {}
                headers = {'User-Agent': 'Mozilla/5.0'}
                prod_url = f'https://api.nike.com/product_feed/threads/v2?filter=language(it)&filter=marketplace(IT)&filter=channelId(d9a5bc42-4b9c-4976-858a-f159cf99c647)&filter=productInfo.merchProduct.styleColor({item.split("/")[-1]})'
                async with session.get(prod_url, headers=headers, ssl=False) as response:
                    item_webpage = await response.json()
                    color = ''
                    for c in [color['name'] for color in item_webpage['objects'][0]['productInfo'][0]['productContent']['colors']]:
                        color += c + ' / '
                    color = color.rstrip(' / ')
                    description = f"Color: {color}\n\n"
                    fullPrice = item_webpage['objects'][0]['productInfo'][0]['merchPrice']['fullPrice']
                    currentPrice = item_webpage['objects'][0]['productInfo'][0]['merchPrice']['currentPrice']
                    dct['title'] = item_webpage['objects'][0]['productInfo'][0]['productContent']['fullTitle']
                    dct['url'] = item
                    dct['curprice'] = currentPrice
                    dct['fullPrice'] = fullPrice
                    dct['colorDescription'] = color
                    products.append(dct)
    else:
        main_url = 'https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=08A180A3B5AAD6BC6470F1A020095EDD&country=it&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(IT)%26filter%3Dlanguage(it)%26filter%3DemployeePrice(true)%26filter%3DattributeIds({})%26anchor%3D{}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D{}&language=en&localizedRangeStr=%7BlowestPrice%7D-%7BhighestPrice%7D'
        products = []
        for i in [60 * i for i in range(0, 20)]:
            try:
                async with session.get(main_url.format(url, i, 60), ssl=False) as response:
                    webpage = await response.json()
                    print(webpage)
                prod = webpage['data']['products']['products']
                products += [{'title' : p['title'], 'url': p['url'].replace('{countryLang}', 'it'), 'curprice': p['price']['currentPrice'], 'fullPrice': p['price']['fullPrice'], 'colorDescription': p['colorDescription']} for p in prod]
            except:
                break
    items = []  
    euro_costs = euro_cost()
    for prod in products:
        try:
            await asyncio.sleep(2)
            item_url = 'https://www.nike.com/' + prod['url']
            #try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            prod_url = f'https://api.nike.com/product_feed/threads/v2?filter=language(it)&filter=marketplace(IT)&filter=channelId(d9a5bc42-4b9c-4976-858a-f159cf99c647)&filter=productInfo.merchProduct.styleColor({prod["url"].split("/")[-1]})'
            async with session.get(prod_url, headers=headers, ssl=False) as response:
                item_webpage = await response.json()
            # название товара
            name = prod['title']
            # артикул
            article = prod['url'].split('/')[-1]
            # цена  
            price = int((prod['curprice'] * (euro_costs + 1)) * float(f"1.{crud.get_category(name=category).margin}")) if prod['curprice'] else None
            
            # описание
            fullPrice = int((prod['fullPrice'] * (euro_costs + 1)) * float(f"1.{crud.get_category(name=category).margin}")) if prod['fullPrice'] else None
            percent = int(100 - (price/fullPrice * 100))
            description = f"Color: {prod['colorDescription']}\n\n"
            description += f'<s>{fullPrice} руб.</s> -{percent}% {price} руб. \n\n'

            # размеры
            skus = item_webpage['objects'][0]['productInfo'][0]['skus']
            availableSkus = {}
            for av_sky in item_webpage['objects'][0]['productInfo'][0]['availableSkus']:
                availableSkus[av_sky['id']] = av_sky['available']
            sizes = 'Sizes: \n'
            list_sizes = ''
            for sku in skus:
                if availableSkus[sku['id']]:
                    sizes += f'<b>{sku["countrySpecifications"][0]["localizedSize"]}</b> '
                    list_sizes += sku["countrySpecifications"][0]["localizedSize"] + ', '
                else:
                    sizes += f'<s>{sku["countrySpecifications"][0]["localizedSize"]}</s> '
            list_sizes = list_sizes.strip(', ')
            if 'TAGLIA UNICA' in sizes:
                sizes = 'Sizes: ONE SIZE\n'
            description += sizes
            # изображения
            if not os.path.exists(f"database/images/{category}"):
                os.mkdir(f"database/images/{category}")

            if not os.path.exists(f"database/images/{category}/{subcategory}"):
                os.mkdir(f"database/images/{category}/{subcategory}")
            
            image_links = [image_func(image) for image in item_webpage['objects'][0]['publishedContent']['nodes'][0]['nodes']]
            if 0 in image_links:
                image_links.remove(0)
            images = ''
            i = products.index(prod)
            for url in image_links[:10]:
                try:
                    num = image_links.index(url) + 1
                    img_path = f"database/images/{category}/{subcategory}/{i}_{name.replace(' ', '_').replace('/', '_')}_{num}.png"
                    images +=  img_path + '\n'
                    if os.path.exists(img_path):
                        continue
                    async with session.get(url, ssl=False) as response:
                        #image = await response.content
                        f = await aiofiles.open(img_path, mode='wb')
                        await f.write(await response.read())
                        await f.close()
                except:
                    continue
            if len(images) < 1:
                continue
            print(item_url)
            items.append([name, description, price, images, prod['colorDescription'], list_sizes, article, item_url])
        except Exception as ex:
            logging.warning(f'{category} pr - {ex}')
    return items



#@db_session()
async def get_nike():
    subcategories = [
        ['Мужчины'],
        ['Обувь мужская', 'Мужчины', 2],
        ['Повседневная обувь мужская', 'Обувь мужская', 3, '193af413-39b0-4d7e-ae34-558821381d3f%2C16633190-45e5-4830-a068-232ac7aea82c%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Jordan кросовки мужские', 'Обувь мужская', 3, '498ac76f-4c2c-4b55-bbdc-dd37011887b1%2C16633190-45e5-4830-a068-232ac7aea82c%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Беговые кросовки мужские', 'Обувь мужская', 3, '49db2f3e-c999-48c2-b5b4-9296635ae75e%2C16633190-45e5-4830-a068-232ac7aea82c%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Футбольные бутсы мужские', 'Обувь мужская', 3, '219e4fa3-73ef-427b-8f93-9d8f51b93443%2C16633190-45e5-4830-a068-232ac7aea82c%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Баскетбольные кросовки мужские', 'Обувь мужская', 3, '4f918ac7-2598-4b21-a46f-99c2db422867%2C16633190-45e5-4830-a068-232ac7aea82c%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Для фитнеса кросовки мужские', 'Обувь мужская', 3, '16633190-45e5-4830-a068-232ac7aea82c%2C7817e756-7721-4cfb-b404-04df79c685e4%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Для скейтбординга кросовки мужские', 'Обувь мужская', 3, 'https://www.nike.com/it/w/uomo-skateboard-scarpe-8mfrfznik1zy7ok'],
        #['Персонализированные кросовки мужские', 'Обувь мужская', 3, '16633190-45e5-4830-a068-232ac7aea82c%2C92be6a0f-24dd-4e2e-87d0-5ce4ade3a923%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Одежда мужская', 'Мужчины', 2],
        ['Свитера и футболки мужские', 'Одежда мужская', 3, 'de314d73-b9c5-4b15-93dd-0bef5257d3b4%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Толстовки мужские', 'Одежда мужская', 3, '9b674c8e-25c9-45c3-8635-c284c07d3d17%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Шорты мужские', 'Одежда мужская', 3, '4a388e98-5844-4fe7-8ed3-a2e6ee5e4333%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Брюки мужские', 'Одежда мужская', 3, '3b5dd430-2183-4019-97cb-5bd8735f10bf%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Спортивные костюмы мужские', 'Одежда мужская', 3, '2507cbc4-f51f-4df9-97f7-3c44b6616b0f%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Ветровки мужские', 'Одежда мужская', 3, '72ff5f48-1b58-4042-8d72-f8a1c057ee06%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Форма мужская', 'Одежда мужская', 3, '4b4f96dd-146c-4c8b-9b95-3d0b7c453387%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Аксессуары мужские', 'Мужчины', 2],
        ['Сумки и рюкзаки мужские', 'Аксессуары мужские', 3, 'e44edc49-f647-4594-a604-dd024d34bec1%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Носки мужские', 'Аксессуары мужские', 3, 'aff7f99d-b113-4fd1-8189-306dfb1aae50%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        
        ['Женщины'],
        ['Обувь женская', 'Женщины', 2],
        ['Повседневная обувь женская', 'Обувь женская', 3, '193af413-39b0-4d7e-ae34-558821381d3f%2C16633190-45e5-4830-a068-232ac7aea82c%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Jordan кросовки женские', 'Обувь женская', 3, '498ac76f-4c2c-4b55-bbdc-dd37011887b1%2C16633190-45e5-4830-a068-232ac7aea82c%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Беговые кросовки женские', 'Обувь женская', 3, '49db2f3e-c999-48c2-b5b4-9296635ae75e%2C16633190-45e5-4830-a068-232ac7aea82c%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Для фитнеса кросовки женские', 'Обувь женская', 3, '16633190-45e5-4830-a068-232ac7aea82c%2C7817e756-7721-4cfb-b404-04df79c685e4%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        #['Персонализированные кросовки женские', 'Обувь женская', 3, '16633190-45e5-4830-a068-232ac7aea82c%2C92be6a0f-24dd-4e2e-87d0-5ce4ade3a923%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Одежда женская', 'Женщины', 2],
        ['Свитера и футболки женские', 'Одежда женская', 3, 'de314d73-b9c5-4b15-93dd-0bef5257d3b4%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Толстовки женские', 'Одежда женская', 3, '9b674c8e-25c9-45c3-8635-c284c07d3d17%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Леггинцы женские', 'Одежда женская', 3, '34374691-44fa-4fb7-a8d2-6ac5764eed1b%2C7baf216c-acc6-4452-9e07-39c2ca77ba32)'],
        ['Шорты женские', 'Одежда женская', 3, '4a388e98-5844-4fe7-8ed3-a2e6ee5e4333%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Брюки женские', 'Одежда женская', 3, '3b5dd430-2183-4019-97cb-5bd8735f10bf%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Спортивные костюмы женские', 'Одежда женская', 3, '3c1b1cc3-bb3f-4f2a-8ada-2724d2f7ad9d%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Ветровки женские', 'Одежда женская', 3, '72ff5f48-1b58-4042-8d72-f8a1c057ee06%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Бюстгальтеры женские', 'Одежда женская', 3, '5c15f4bd-dc38-4ec7-85a5-5ace48b5c335%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Юбки и патья женские', 'Одежда женская', 3, 'cd7ee063-a9d4-43ea-a126-ef74582fdb7f%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Купальники женские', 'Одежда женская', 3, 'https://www.nike.com/it/w/donna-costumi-e-accessori-da-mare-5e1x6zq3un'],
        ['Аксессуары женские', 'Женщины', 2],
        ['Рюкзаки и сумки женские', 'Аксессуары женские', 3, 'e44edc49-f647-4594-a604-dd024d34bec1%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Носки женские', 'Аксессуары женские', 3, 'aff7f99d-b113-4fd1-8189-306dfb1aae50%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        
        ['Дети'],
        ['Обувь детская', 'Дети', 2],
        ['Повседневная обувь детская', 'Обувь детская', 3, '193af413-39b0-4d7e-ae34-558821381d3f%2C16633190-45e5-4830-a068-232ac7aea82c%2C145ce13c-5740-49bd-b2fd-0f67214765b3)'],
        ['Кросовки Jordan детские', 'Обувь детская', 3, '498ac76f-4c2c-4b55-bbdc-dd37011887b1%2C16633190-45e5-4830-a068-232ac7aea82c%2C145ce13c-5740-49bd-b2fd-0f67214765b3'],
        ['Футбольные бутсы детские', 'Обувь детская', 3, '219e4fa3-73ef-427b-8f93-9d8f51b93443%2C16633190-45e5-4830-a068-232ac7aea82c%2C145ce13c-5740-49bd-b2fd-0f67214765b3'],
        ['Беговые кросовки детские', 'Обувь детская', 3, '49db2f3e-c999-48c2-b5b4-9296635ae75e%2C16633190-45e5-4830-a068-232ac7aea82c%2C145ce13c-5740-49bd-b2fd-0f67214765b3'],
        ['Баскетбольные кросовки детские', 'Обувь детская', 3, 'https://www.nike.com/it/w/bambini-basket-scarpe-3glsmzv4dhzy7ok'],
        ['Одежда детская', 'Дети', 2],
        ['Свитера и футболки детские', 'Одежда детская', 3, 'de314d73-b9c5-4b15-93dd-0bef5257d3b4%2C145ce13c-5740-49bd-b2fd-0f67214765b3'],
        ['Толстовки детские', 'Одежда детская', 3, '145ce13c-5740-49bd-b2fd-0f67214765b3%2C9b674c8e-25c9-45c3-8635-c284c07d3d17'],
        ['Спортивные костюмы детские', 'Одежда детская', 3, '2507cbc4-f51f-4df9-97f7-3c44b6616b0f%2C145ce13c-5740-49bd-b2fd-0f67214765b3'],
        ['Шорты детские', 'Одежда детская', 3, '4a388e98-5844-4fe7-8ed3-a2e6ee5e4333%2C145ce13c-5740-49bd-b2fd-0f67214765b3'],
        ['Брюки и леггинцы детские', 'Одежда детская', 3, '3b5dd430-2183-4019-97cb-5bd8735f10bf%2C145ce13c-5740-49bd-b2fd-0f67214765b3'],
        ['Куртки детские', 'Одежда детская', 3, '72ff5f48-1b58-4042-8d72-f8a1c057ee06%2C145ce13c-5740-49bd-b2fd-0f67214765b3'],
        ['Форма детская', 'Одежда детская', 3, '4b4f96dd-146c-4c8b-9b95-3d0b7c453387%2C145ce13c-5740-49bd-b2fd-0f67214765b3'],
        ['Бюстгальтеры детские', 'Одежда детская', 3, 'https://www.nike.com/it/w/bambina-reggiseni-sportivi-3aqegz40qgm'],
        ['Юбки и платья детские', 'Одежда детская', 3, 'https://www.nike.com/it/w/bambini-gonne-abiti-8y3qpzv4dh'],
        ['Аскессуары детские', 'Дети', 2],
        ['Рюкзаки и сумки детские', 'Аскессуары детские', 3, 'https://www.nike.com/it/w/bambini-borse-zaini-9xy71zv4dh'],
        ['Головные уборы детские', 'Аскессуары детские', 3, 'https://www.nike.com/it/w/bambini-cappelli-berretti-52r49zv4dh'],

        ###
        ['Аутлет'],
        ['Мужчины аутлет', 'Аутлет', 2],
        ['Обувь мужская аутлет', 'Мужчины аутлет', 3, '5b21a62a-0503-400c-8336-3ccfbff2a684%2C16633190-45e5-4830-a068-232ac7aea82c%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],        
        ['Одежда мужская аутлет', 'Мужчины аутлет', 3, '5b21a62a-0503-400c-8336-3ccfbff2a684%2Ca00f0bb2-648b-4853-9559-4cd943b7d6c6%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],
        ['Аксессуары мужские аутлет', 'Мужчины аутлет', 3, 'fa863563-4508-416d-bae9-a53188c04937%2C5b21a62a-0503-400c-8336-3ccfbff2a684%2C0f64ecc7-d624-4e91-b171-b83a03dd8550'],

        ['Женщины аутлет', 'Аутлет', 2],
        ['Обувь женская аутлет', 'Женщины аутлет', 3, '5b21a62a-0503-400c-8336-3ccfbff2a684%2C16633190-45e5-4830-a068-232ac7aea82c%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Одежда женская аутлет', 'Женщины аутлет', 3, '5b21a62a-0503-400c-8336-3ccfbff2a684%2Ca00f0bb2-648b-4853-9559-4cd943b7d6c6%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],
        ['Аксессуары женские аутлет', 'Женщины аутлет', 3, 'fa863563-4508-416d-bae9-a53188c04937%2C5b21a62a-0503-400c-8336-3ccfbff2a684%2C7baf216c-acc6-4452-9e07-39c2ca77ba32'],

        ['Дети аутлет', 'Аутлет', 2], 
        ['Обувь детская аутлет', 'Дети аутлет', 3, '5b21a62a-0503-400c-8336-3ccfbff2a684%2C16633190-45e5-4830-a068-232ac7aea82c%2C145ce13c-5740-49bd-b2fd-0f67214765b3'],
        ['Одежда детская аутлет', 'Дети аутлет', 3, '5b21a62a-0503-400c-8336-3ccfbff2a684%2C145ce13c-5740-49bd-b2fd-0f67214765b3%2Ca00f0bb2-648b-4853-9559-4cd943b7d6c6'],
        ['Аскессуары детские аутлет', 'Дети аутлет', 3, 'https://www.nike.com/it/w/bambini-outlet-3yaepzv4dh'],
    ]
    cat_name = 'NIKE'
    for subcategory in subcategories:
        if len(subcategory) == 1:
            s = crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            continue
        elif not isinstance(subcategory[-1], str):
            if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
                crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue

        logging.info(f'Starting NIKE: {subcategory[0]}')
        async with aiohttp.ClientSession(trust_env=True) as session:
            if subcategory[-1].startswith('http'):
                async with session.get(subcategory[-1], ssl=False) as response:
                    webpage = await response.text()
                    soup = bs(webpage, 'html.parser')
                    items = [item.find('figure').find('a').get('href') for item in soup.find_all('div', 'product-card__body')]
                    products = []
                    for item in items:
                        dct = {}
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        prod_url = f'https://api.nike.com/product_feed/threads/v2?filter=language(it)&filter=marketplace(IT)&filter=channelId(d9a5bc42-4b9c-4976-858a-f159cf99c647)&filter=productInfo.merchProduct.styleColor({item.split("/")[-1]})'
                        async with session.get(prod_url, headers=headers, ssl=False) as response:
                            item_webpage = await response.json()
                            color = ''
                            for c in [color['name'] for color in item_webpage['objects'][0]['productInfo'][0]['productContent']['colors']]:
                                color += c + ' / '
                            color = color.rstrip(' / ')
                            description = f"Color: {color}\n\n"
                            fullPrice = item_webpage['objects'][0]['productInfo'][0]['merchPrice']['fullPrice']
                            currentPrice = item_webpage['objects'][0]['productInfo'][0]['merchPrice']['currentPrice']
                            dct['title'] = item_webpage['objects'][0]['productInfo'][0]['productContent']['fullTitle']
                            if dct['title'] == 'Gift card Nike':
                                continue
                            dct['url'] = item
                            dct['curprice'] = currentPrice
                            dct['fullPrice'] = fullPrice
                            dct['colorDescription'] = color
                            products.append(dct)
        
            else:
                main_url = 'https://api.nike.com/cic/browse/v2?queryid=products&country=it&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(IT)%26filter%3Dlanguage(it)%26filter%3DemployeePrice(true)%26filter%3DattributeIds({})%26anchor%3D{}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D{}&language=en&localizedRangeStr=%7BlowestPrice%7D-%7BhighestPrice%7D'
                products = []
                for i in [60 * i for i in range(0, 20)]:
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        async with session.get(main_url.format(subcategory[-1], i, 60), headers=headers, ssl=False) as response:
                            webpage = await response.json()
                            prod = webpage['data']['products']['products']
                            products += [{'title' : p['title'], 'url': p['url'].replace('{countryLang}', 'it'), 'curprice': p['price']['currentPrice'], 'fullPrice': p['price']['fullPrice'], 'colorDescription': p['colorDescription']} for p in prod]
                    except:
                        break
                
            items = []  
            euro_costs = euro_cost()
            for prod in products:
                try:
                    #await asyncio.sleep(2)
                    item_url = 'https://www.nike.com/' + prod['url']
                    #try:
                    
                    prod_url = f'https://api.nike.com/product_feed/threads/v2?filter=language(it)&filter=marketplace(IT)&filter=channelId(d9a5bc42-4b9c-4976-858a-f159cf99c647)&filter=productInfo.merchProduct.styleColor({prod["url"].split("/")[-1]})'
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    async with session.get(prod_url, headers=headers, ssl=False) as response:
                        item_webpage = await response.json()
                        
                    # название товара
                    name = prod['title']
                    #print(name)
                    # артикул
                    article = prod['url'].split('/')[-1]
                    # цена  
                    price = int((prod['curprice'] * (euro_costs + 1)) * float(f"1.{crud.get_category(name=cat_name).margin}")) if prod['curprice'] else None
                    # описание
                    fullPrice = int((prod['fullPrice'] * (euro_costs + 1)) * float(f"1.{crud.get_category(name=cat_name).margin}")) if prod['fullPrice'] else None
                    percent = int(100 - (price/fullPrice * 100))
                    description = f"Color: {prod['colorDescription']}\n\n"
                    if fullPrice > price:
                        description += f'<s>{fullPrice} руб.</s> -{percent}% {price} руб. \n\n'

                    # размеры
                    try:
                        skus = item_webpage['objects'][0]['productInfo'][0]['skus']
                        availableSkus = {}
                        for av_sky in item_webpage['objects'][0]['productInfo'][0]['availableSkus']:
                            availableSkus[av_sky['id']] = av_sky['available']
                        sizes = 'Sizes: \n'
                        list_sizes = ''
                        for sku in skus:
                            if availableSkus[sku['id']]:
                                sizes += f'<b>{sku["countrySpecifications"][0]["localizedSize"]}</b> '
                                list_sizes += sku["countrySpecifications"][0]["localizedSize"] + ', '
                            else:
                                sizes += f'<s>{sku["countrySpecifications"][0]["localizedSize"]}</s> '
                        list_sizes = list_sizes.strip(', ')
                        if 'TAGLIA UNICA' in sizes:
                            sizes = 'Sizes: ONE SIZE\n'
                        description += sizes
                    except:
                        pass
                    
                    image_links = [image_func(image) for image in item_webpage['objects'][0]['publishedContent']['nodes'][0]['nodes']]
                    # изображения
                    if not os.path.exists(f"database/images/{cat_name}"):
                        os.mkdir(f"database/images/{cat_name}")

                    if not os.path.exists(f"database/images/{cat_name}/{subcategory[0]}"):
                        os.mkdir(f"database/images/{cat_name}/{subcategory[0]}")
                    
                    if 0 in image_links:
                        image_links.remove(0)

                    i = products.index(prod) + 1
                    images = ''
                    #print(image_links)
                    for url in image_links[:10]:
                        #print(url)
                        try:
                            num = image_links.index(url) + 1
                            img_path = f"database/images/{cat_name}/{subcategory[0]}/{i}_{name.replace(' ', '_').replace('/', '_')}_{num}.png"
                            images +=  img_path + '\n'
                            if os.path.exists(img_path):
                                continue
                            async with session.get(url, ssl=False) as response:
                                #image = await response.content
                                f = await aiofiles.open(img_path, mode='wb')
                                await f.write(await response.read())
                                await f.close()
                        except:
                            continue
                    if len(images) < 1:
                        continue
                    items.append([name, description, price, images, list_sizes, article, item_url])
                except Exception as ex:
                    logging.warning(f'{cat_name} pr - {ex}')
        
        if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
            crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        
        crud.create_products(category=cat_name, subcategory=subcategory[0], items=items)
        logging.info(f'Canceled {cat_name} {subcategory[0]} added {len(items)} products')

    await bot.send_message(227184505, f'{cat_name} закончил парсинг')


async def get_golcegabbana():
    subcategories = [
        ['Женщины'],
        ['Женская одежда', 'Женщины', 2],
        ['Платья женские', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/dresses-jumpsuits'],
        ['Топы женские', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/top'],
        ['Юбки женские', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/skirt'],
        ['Брюки и шорты женские', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/pants'],
        ['Пиджаки женские', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/jacket'],
        ['Пальто женские', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/coat'],
        ['Рубашки женские', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/shirts-woman'],
        ['Джерси женские', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/jersey'],
        ['Спортивные комтюмы женские', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/sportswear-1'],
        ['Трикотаж женский', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/knitwear'],
        ['Бюстгальтеры женские', 'Женская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/bra'],

        ['Женская обувь', 'Женщины', 2],
        ['Кросовки женские', 'Женская обувь', 3, 'https://dolcegabbanaprivatesales.com/collections/sneakers-woman'],
        ['Туфли женские', 'Женская обувь', 3, 'https://dolcegabbanaprivatesales.com/collections/elegant-woman'],

        ['Женские аксессуары', 'Женщины', 2],
        ['Бижутерия женская', 'Женские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/bijoux'],
        ['Платки женские', 'Женские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/foulard'],
        ['Кожаные изделия женские', 'Женские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/small-leather-goods-woman'],
        ['Очки женские', 'Женские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/eyewear-woman'],
        ['Вязаные аксессуары женские', 'Женские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/knit-accessories'],
        ['Ремни женские', 'Женские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/belts'],
        ['Мини-сумки женские', 'Женские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/mini-bags'],
        
        ['Мужчины'],
        ['Мужская одежда', 'Мужчины', 2],
        ['Брюки и шорты мужские', 'Мужская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/pants-man'],
        ['Пиджаки мужские', 'Мужская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/jacket-1'],
        ['Джинсы мужские', 'Мужская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/denim-tc'],
        ['Трикотаж мужской', 'Мужская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/knitwear-1'],
        ['Верхняя одежда мужская', 'Мужская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/outerwear'],
        ['Рубашки мужские', 'Мужская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/shirts'],
        ['Джерси мужские', 'Мужская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/jersey-man'],
        ['Плавки мужские', 'Мужская одежда', 3, 'https://dolcegabbanaprivatesales.com/collections/beachwear-1'],
        
        ['Мужская обувь', 'Мужчины', 2],
        ['Тапочки мужские', 'Мужская обувь', 3, 'https://dolcegabbanaprivatesales.com/collections/rubber'],
        ['Кросовки мужские', 'Мужская обувь', 3, 'https://dolcegabbanaprivatesales.com/collections/sneakers'],
        ['Туфли мужские', 'Мужская обувь', 3, 'https://dolcegabbanaprivatesales.com/collections/elegant'],
        ['Эспадрильи мужские', 'Мужская обувь', 3, 'https://dolcegabbanaprivatesales.com/collections/espadrilles-woman'],
        
        ['Мужские аксессуары', 'Мужчины', 2],
        ['Рюкзаки мужские', 'Мужские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/backpacks-man'],
        ['Маленькие кожаные изделия мужские', 'Мужские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/small-leather-goods'],
        ['Бижутерия мужская', 'Мужские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/bijoux-man'],
        ['Текстильные аксессуары мужские', 'Мужские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/textile-accessories'],
        ['Очки мужские', 'Мужские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/eyewear'],
        ['Ремни мужские', 'Мужские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/belts-1'],
        ['Вязанные аксессуары мужские', 'Мужские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/knit-accessories-man'],
        ['Кожаные изделия мужские', 'Мужские аксессуары', 3, 'https://dolcegabbanaprivatesales.com/collections/leather-man'],
        
        ['Дети'],
        ['Для младенцев (девоки)', 'Дети', 2, 'https://dolcegabbanaprivatesales.com/collections/app-newborn-female'],
        ['Для младенцев (мальчики)', 'Дети', 2, 'https://dolcegabbanaprivatesales.com/collections/apparel-newborn-male'],
        ['Для малышей (девочки)', 'Дети', 2, 'https://dolcegabbanaprivatesales.com/collections/baby-female-1'],
        ['Для малышей (мальчики)', 'Дети', 2, 'https://dolcegabbanaprivatesales.com/collections/baby-male'],
        ['Для детей 2-12 лет', 'Дети', 2, 'https://dolcegabbanaprivatesales.com/collections/baby-2-12-years'],
        ['Для новорожденных (3-30 месяцев)', 'Дети', 2, 'https://dolcegabbanaprivatesales.com/collections/kids-apparel'],
        ['Детские аксессуары', 'Дети', 2, 'https://dolcegabbanaprivatesales.com/collections/kids-accessories'],
        ['Детские кожаные изделия', 'Дети', 2, 'https://dolcegabbanaprivatesales.com/collections/baby-leather'],
        ['Детская обувь', 'Дети', 2, 'https://dolcegabbanaprivatesales.com/collections/baby-shoes']
    ]
    cat_name = 'Dolce&Gabanna Outlet'
    for subcategory in subcategories:
        if not str(subcategory[-1]).startswith('http'):
            if len(subcategory) == 1:
                crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            else:
                if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                    parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
                    crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue
        # logging
        #url = 'https://dolcegabbanaprivatesales.com/account/login/'
        #s = requests.Session()
        #r = s.get(url)
        #csrf_token = r.cookies['_secure_session_id']#Cookie _secure_session_id
        #data = {
        #    'login': os.getenv('DGLogin'),
        #    'password': os.getenv('DGPassword'),
        #    'csrfmiddlewaretoken': csrf_token
        #}
        #d = s.post(url, data=data, headers=dict(Referer=url))
        #dd = s.get('https://dolcegabbanaprivatesales.com/collections/dresses-jumpsuits')


        logging.info(f'Starting Dolce&Gabanna: {subcategory[0]}')
        async with aiohttp.ClientSession(trust_env=True) as session:
            items_urls = []
            for i in range(1, 100):
                url = subcategory[-1] + f'?page={i}'
                async with session.get(url, ssl=False) as response:
                    webpage = await response.text()
                    #print(response.status)
                    soup = bs(webpage, 'html.parser')
                    items = [item.find('a').get('href') for item in soup.find_all('div', 'product-item small--one-half medium--one-half large-up--one-quarter')]
                    if len(items) == 0:
                        break
                    items_urls += items
                await asyncio.sleep(2)
        
        items = []
        euro_costs = euro_cost()
        for url in items_urls:
            try:
                await asyncio.sleep(2)
                async with aiohttp.ClientSession(trust_env=True) as session:
                    async with session.get('https://dolcegabbanaprivatesales.com' + url, ssl=False) as response:
                        item_url = 'https://dolcegabbanaprivatesales.com' + url
                        webpage = await response.text()
                        soup = bs(webpage, 'html.parser')
                        title = soup.find('h1', 'product__title').text
                        
                        try:
                            old_price = soup.find('s', 'product__price--strike').text.strip('\n').strip(' ').strip('\n').strip(' ').strip('\n').strip(' ').strip('€').replace('.', '').replace(',', '.')
                            #print(old_price)
                            old_price = int((float(old_price) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Dolce&Gabanna Outlet').margin}"))
                            #print(old_price)
                        except:
                            old_price = None
                        current_price = soup.find('span', 'product__price--sale').text.strip('\n').strip(' ').strip('€').replace('.', '').replace(',', '.').strip('\n').strip(' ')
                        #print(current_price)
                        current_price = int((float(current_price) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Dolce&Gabanna Outlet').margin}"))
                        #print(current_price)
                        
                        #print(percent)
                        description = ''
                        #description = soup.find('div', 'product-description rte').text.strip('\n').strip(' ').strip('\n')
                        if old_price:
                            percent = int(100 - float(current_price)/(float(old_price)/100))
                            description = description[:700] + f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                            
                        #print(description)
                        sizes = [size.text.replace('\n', '').strip(' ') for size in soup.find_all('div', 'variant-field')]
                        try:
                            if int(sizes[0]) > 100:
                                sizes = [str(int(size)/100) for size in sizes]
                        except:
                            pass
                        list_sizes = ''
                        for size in sizes:
                            list_sizes += f'{size}, '
                        list_sizes = list_sizes.strip(', ')
                        description += f'\n\nРазмеры: {list_sizes}'
                        #print(list_sizes)
                        article = url.split('/')[-1]

                        # изображения
                        if not os.path.exists(f"database/images/Dolce&Gabanna Outlet"):
                            os.mkdir(f"database/images/Dolce&Gabanna Outlet")

                        if not os.path.exists(f"database/images/Dolce&Gabanna Outlet/{subcategory[0]}"):
                            os.mkdir(f"database/images/Dolce&Gabanna Outlet/{subcategory[0]}")
                        image_links = ['https:' + photo.find('img', {'style': "display: none;"}).get('data-src') for photo in soup.find_all('div', ['product__photo', 'product__photo media--hidden'])]
                        
                        i = items_urls.index(url) + 1
                        images = ''
                        
                        for url in image_links[:10]:
                            try:
                                num = image_links.index(url) + 1
                                img_path = f"database/images/Dolce&Gabanna/{subcategory[0]}/{i}_{title.replace(' ', '_').replace('/', '_')}_{num}.png"
                                if not os.path.exists(img_path):
                                    async with session.get(url, ssl=False) as response:
                                        f = await aiofiles.open(img_path, mode='wb')
                                        await f.write(await response.read())
                                        await f.close()
                                images +=  img_path + '\n'
                            except:
                                continue
                        
                        if len(images) < 1:
                            continue
                        #print(images)
                        items.append([title, description, current_price, images, list_sizes, article, item_url])
                        #logging.info(title)
                        #print([title, description, current_price, images, list_sizes, article])
            except Exception as ex:
                logging.warning(f'Dolce&Gabanna pr - {ex}')
        #crud.del_products(subcategory=subcategory, category='Dolce&Gabanna')
        #try:
        #    not_deleted_items = [product.article for product in crud.get_product(category_id=crud.get_category(name='Dolce&Gabanna').id, subcategory_id=crud.get_subcategory(name=subcategory).id)]
        #except:
        #    not_deleted_items = []
        #logging.info(items)
        if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
            crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        
        crud.create_products(category=cat_name, subcategory=subcategory[0], items=items)

        logging.info(f'Canceled {cat_name} {subcategory[0]} added {len(items)} products') 
    await bot.send_message(227184505, f'{cat_name} закончил парсинг')


async def get_coach():
    subcategories = [
        ['Женщины'],
        ['Сумки женские', 'Женщины', 2],
        ['Наплечные сумки женские', 'Сумки женские', 3, 'https://it.coach.com/api/get-shop/donna/borse/tracolle{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Cумки крос-боди женские', 'Сумки женские', 3, 'https://it.coach.com/api/shop/donna/borse/borse-a-tracolla{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Сумки-ведра женские', 'Сумки женские', 3, 'https://it.coach.com/api/shop/donna/borse/borse-a-secchiello{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Большие сумки женские', 'Сумки женские', 3, 'https://it.coach.com/api/shop/donna/borse/borse-larghe{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Клатчи женские', 'Сумки женские', 3, 'https://it.coach.com/api/shop/donna/borse/pochette{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Рюкзаки женские', 'Сумки женские', 3, 'https://it.coach.com/api/shop/donna/borse/zaini{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Фирменные сумки женские', 'Сумки женские', 3, 'https://it.coach.com/api/shop/donna/borse/borse-signature{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Кожаные изделия женские', 'Женщины', 2],
        ['Наплечные кошельки женские', 'Кожаные изделия женские', 3, 'https://it.coach.com/api/shop/donna/piccoli-accessori-in-pelle/portafogli-con-tracolla{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Большие кошельки женские', 'Кожаные изделия женские', 3, 'https://it.coach.com/api/shop/donna/piccoli-accessori-in-pelle/portafogli-grandi{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Маленькие кошельки женские', 'Кожаные изделия женские', 3, 'https://it.coach.com/api/shop/donna/piccoli-accessori-in-pelle/portafogli-piccoli{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Наручные саше женские', 'Кожаные изделия женские', 3, 'https://it.coach.com/api/shop/donna/piccoli-accessori-in-pelle/bustine-da-polso{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Кардходлеры женские', 'Кожаные изделия женские', 3, 'https://it.coach.com/api/shop/donna/piccoli-accessori-in-pelle/porta-carte-di-credito{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Одежда женская', 'Женщины', 2],
        ['Пальто и куртки женские', 'Одежда женская', 3, 'https://it.coach.com/api/shop/donna/pret-a-porter/cappotti-e-giacche{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Рубашки и свитеры женские', 'Одежда женская', 3, 'https://it.coach.com/api/shop/donna/pret-a-porter/maglioni-e-felpe-con-cappuccio{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Топы и футболки женские', 'Одежда женская', 3, 'https://it.coach.com/api/shop/donna/pret-a-porter/top-e-magliette{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Платья женские', 'Одежда женская', 3, 'https://it.coach.com/api/shop/donna/pret-a-porter/abiti{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Шорты и юбки женские', 'Одежда женская', 3, 'https://it.coach.com/api/shop/donna/pret-a-porter/pantaloni{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Обувь женская', 'Женщины', 2],
        ['Сандалии женские', 'Обувь женская', 3, 'https://it.coach.com/api/shop/donna/calzature/sandali{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Балетки женские', 'Обувь женская', 3, 'https://it.coach.com/api/shop/donna/calzature/ballerine{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Туфли на каблуке женские', 'Обувь женская', 3, 'https://it.coach.com/api/shop/donna/calzature/scarpe-con-tacco{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Кросовки женские', 'Обувь женская', 3, 'https://it.coach.com/api/shop/donna/calzature/trainer{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Ботинки женские', 'Обувь женская', 3, 'https://it.coach.com/api/shop/donna/calzature/stivali{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Аксессуары женские', 'Женщины', 2],
        ['Драгоценности женские', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/gioielli{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Ремни женские', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/cinture{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Часы женские', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/orologi{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Шапки, шарфы и перчатки женские', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/cappelli-sciarpe-e-guanti{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Кулоны и брелки женские', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/ciondoli-per-borsa-e-portachiavi{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Аксессуары для техники и путешествий женские', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/accessori-tecnologici-e-da-viaggio{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Очки женские', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/occhiali-da-sole{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Ремни для сумок женские', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/tracolle-per-borsa{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Уход за продукцией (жен)', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/cura-dei-prodotti{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Духи женские', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/fragranza{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Мужчины'],
        ['Сумки мужские', 'Мужчины', 2],
        ['Фирменные сумки мужские', 'Сумки мужские', 3, 'https://it.coach.com/api/shop/uomo/borse/borse-signature{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Рюкзаки мужские', 'Сумки мужские', 3, 'https://it.coach.com/api/shop/uomo/borse/zaini{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Большие сумки мужские', 'Сумки мужские', 3, 'https://it.coach.com/api/shop/uomo/borse/borse-larghe-e-borsoni{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Поясные сумки мужские', 'Сумки мужские', 3, 'https://it.coach.com/api/shop/uomo/borse/borse-a-cintura{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Портфели мужские', 'Сумки мужские', 3, 'https://it.coach.com/api/shop/uomo/borse/valigette{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Папки мужские', 'Сумки мужские', 3, 'https://it.coach.com/api/shop/uomo/borse/cartelle{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Одежда мужская', 'Мужчины', 2],
        ['Пальто и куртки мужские', 'Одежда мужская', 3, 'https://it.coach.com/api/shop/uomo/pret-a-porter/cappotti-e-giacche{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Одежда (верх и низ) мужские', 'Одежда мужская', 3, 'https://it.coach.com/api/shop/uomo/pret-a-porter/pezzi-di-sopra-e-sotto{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Обувь мужская', 'Мужчины', 2],
        ['Сандалии мужские', 'Обувь мужская', 3, 'https://it.coach.com/api/shop/uomo/calzature/sandali{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Повседневная обувь мужские', 'Обувь мужская', 3, 'https://it.coach.com/api/shop/uomo/calzature/casual{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Ботинки мужские', 'Обувь мужская', 3, 'https://it.coach.com/api/shop/uomo/calzature/stivali{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Аксессуары мужские', 'Мужчины', 2],
        ['Маски мужские', 'Аксессуары мужские', 3, 'https://it.coach.com/api/shop/uomo/accessori/mascherine{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Ремни мужские', 'Аксессуары мужские', 3, 'https://it.coach.com/api/shop/uomo/accessori/cinture{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Брелоки мужские', 'Аксессуары мужские', 3, 'https://it.coach.com/api/shop/uomo/accessori/portachiavi{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Солнечные очки мужские', 'Аксессуары мужские', 3, 'https://it.coach.com/api/shop/uomo/accessori/occhiali-da-sole{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Аксессуары для техники и путешествий мужские', 'Аксессуары мужские', 3, 'https://it.coach.com/api/shop/uomo/accessori/accessori-tecnologici-e-da-viaggio{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Часы мужские', 'Аксессуары мужские', 3, 'https://it.coach.com/api/shop/uomo/accessori/orologi{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],        ['Маски женские', 'Аксессуары женские', 3, 'https://it.coach.com/api/shop/donna/accessori/mascherine{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ['Духи мужские', 'Аксессуары мужские', 3, 'https://it.coach.com/api/shop/uomo/accessori/fragranza{}&__v__=Y-sbL5i1aIu4e3dEx9wRm&locale=it_IT'],
        ]
    cat_name = 'COACH'
    for subcategory in subcategories:
        if subcategory[0] != 'Большие сумки мужские':
            continue
        if not str(subcategory[-1]).startswith('http'):
            if len(subcategory) == 1:
                crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            else:
                if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                    parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
                    crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue
    
        logging.info(f'Starting {cat_name}: {subcategory[0]}')
        async with aiohttp.ClientSession(trust_env=True) as session:
            items = []
            for i in range(1, 100):
                async with session.get(subcategory[-1].format(f'?page={i}'), ssl=False) as response:
                    webpage = await response.json()
                    if len(webpage['pageData']['products']) > 0:
                        items += webpage['pageData']['products']
                    else:
                        break
                    
            products = []
            euro_costs = euro_cost()
            for item in items:
                #try:
                await asyncio.sleep(2)
                for color_item in item['colors']:
                    item_url = 'https://it.coach.com/it_IT' + item['url']
                    print(item_url)
                    title = item['name'] + ' ' + color_item['text']
                    print(title)
                    color = color_item['text']
                    #print(color)
                    
                    current_price = int((float(item['prices']['currentPrice']) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='COACH').margin}"))
                    try:
                        old_price = int((float(item['prices']['regularPrice']) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='COACH').margin}"))
                        percent = int(100 - float(current_price)/(float(old_price)/100))
                    except:
                        old_price = None
                    
                    #print(price)
                    async with session.get(f"https://it.coach.com/api/get-suggestions-products?ids={item['id'].replace(' ', '+')}%2CCF925+B4%2FWN%2CCE897+LJN++S%2CCG798+BLK++XL&locale=it_IT&__v__=0vd2xlsFnzxBsryah6o6X", ssl=False) as response:
                        item_webpage = await response.json()
                    #print(soup)
                    description = ''
                    #description = item_webpage['productsData'][0]['longDescription'].replace('<li>', '').replace('</li>', '').replace('<ul>', '').replace('</ul>', '')
                    if old_price:
                        description = description[:700] + f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                    list_sizes = ''
                    try:
                        sizes = [size['value'] for size in item_webpage['productsData'][0]['variationGroup'][0]['variationAttributes'][1]['values'] if size['orderable']]
                        list_sizes = ''
                        for size in sizes:
                            list_sizes += size + ', '
                        list_sizes = list_sizes.strip(', ')

                        description += '\n\nРазмеры:\n' + list_sizes
                    except:
                        pass
                    #print(description)
                    article = item['masterId'] + ' ' + color
                    #print(article)
                    image_links = [image['src'] for image in color_item['media']['full']]
                    # изображения
                    if not os.path.exists(f"database/images/{cat_name}"):
                        os.mkdir(f"database/images/{cat_name}")

                    if not os.path.exists(f"database/images/{cat_name}/{subcategory[0]}"):
                        os.mkdir(f"database/images/{cat_name}/{subcategory[0]}")

                    i = items.index(item) + 1
                    images = ''
                    
                    for url in image_links[:10]:
                        try:
                            num = image_links.index(url) + 1
                            img_path = f"database/images/{cat_name}/{subcategory[0]}/{i}_{title.replace(' ', '_').replace('/', '_')}_{num}.png"
                            if not os.path.exists(img_path):
                                async with session.get(url, ssl=False) as response:
                                    f = await aiofiles.open(img_path, mode='wb')
                                    await f.write(await response.read())
                                    await f.close()
                            images +=  img_path + '\n'
                        except:
                            continue
                    products.append([title, description, current_price, images, list_sizes, article, item_url])
                #except Exception as ex:
                #    logging.warning(f'{cat_name} pr - {ex}')

        if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
            crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        
        crud.create_products(category=cat_name, subcategory=subcategory[0], items=products)

        logging.info(f'Canceled {cat_name} {subcategory[0]} added {len(products)} products') 
    await bot.send_message(227184505, f'{cat_name} закончил парсинг')


async def get_asics():
    subcategories = [
        ['Мужчины'],
        ['Обувь мужская', 'Мужчины', 2],
        ['Беговые кросовки мужские', 'Обувь мужская', 3, 'https://www.asics.com/it/en-it/mens-running-shoes/c/as10201000/?sz=96&start={}'],
        ['Туристические кросовки мужские', 'Обувь мужская', 3, 'https://www.asics.com/it/en-it/mens-trail-running-hiking-shoes/c/as10201010/?sz=96&start={}'],
        ['Теннисные кросовки мужские', 'Обувь мужская', 3, 'https://www.asics.com/it/en-it/mens-tennis-shoes/c/as10203000/?sz=96&start={}'],
        ['Волейбольные кросовки мужские', 'Обувь мужская', 3, 'https://www.asics.com/it/en-it/mens-volleyball-shoes/c/as10204000/?sz=96&start={}'],
        ['Гандбольные кросовки мужские', 'Обувь мужская', 3, 'https://www.asics.com/it/en-it/mens-handball-shoes/c/as10216000/?sz=96&start={}'],
        ['Падельные кросовки мужские', 'Обувь мужская', 3, 'https://www.asics.com/it/en-it/mens-padel-shoes/c/as10205000/?sz=96&start={}'],
        ['Повседневные кросовки мужские', 'Обувь мужская', 3, 'https://www.asics.com/it/en-it/sportstyle-men-shoes/c/as10219000/?sz=96&start={}'],

        ['Одежда мужская', 'Мужчины', 2],
        ['Футболки без рукава мужские', 'Одежда мужская', 3, 'https://www.asics.com/it/en-it/mens-tank-tops/c/as10301010/?sz=96&start={}'],
        ['Футболки мужские', 'Одежда мужская', 3, 'https://www.asics.com/it/en-it/mens-short-sleeve-shirts/c/as10301040/?sz=96&start={}'],
        ['Лонгсливы мужские', 'Одежда мужская', 3, 'https://www.asics.com/it/en-it/mens-long-sleeve-shirts/c/as10301050/?sz=96&start={}'],
        ['Худи и свитшоты мужские', 'Одежда мужская', 3, 'https://www.asics.com/it/en-it/mens-hoodies-sweatshirts/c/as10301020/?sz=96&start={}'],
        ['Куртки мужские', 'Одежда мужская', 3, 'https://www.asics.com/it/en-it/mens-jackets-vests/c/as10301030/?sz=96&start={}'],
        ['Леггинцы мужские', 'Одежда мужская', 3, 'https://www.asics.com/it/en-it/mens-tights-leggings/c/as10302010/?sz=96&start={}'],
        ['Шорты мужские', 'Одежда мужская', 3, 'https://www.asics.com/it/en-it/mens-shorts/c/as10302020/?sz=96&start={}'],
        ['Штаны мужские', 'Одежда мужская', 3, 'https://www.asics.com/it/en-it/mens-pants/c/as10302030/?sz=96&start={}'],
        
        ['Аксессуары мужские', 'Мужчины', 2],
        ['Головные уборы мужские', 'Аксессуары мужские', 3, 'https://www.asics.com/it/en-it/mens-hats-headbands-beanies/c/as10401000/?sz=96&start={}'],
        ['Перчатки мужские', 'Аксессуары мужские', 3, 'https://www.asics.com/it/en-it/mens-gloves/c/as10405000/?sz=96&start={}'],
        ['Носки мужские', 'Аксессуары мужские', 3, 'https://www.asics.com/it/en-it/mens-socks/c/as10402000/?sz=96&start={}'],
        ['Сумки и рюкзаки мужские', 'Аксессуары мужские', 3, 'https://www.asics.com/it/en-it/mens-bags-packs/c/as10404000/?sz=96&start={}'],
        ['Экипировка мужские', 'Аксессуары мужские', 3, 'https://www.asics.com/it/en-it/mens-equipment/c/as10408000/?sz=96&start={}'],

        ['Женщины'],
        ['Обувь женская', 'Женщины', 2],
        ['Беговые кросовки женские', 'Обувь женская', 3, 'https://www.asics.com/it/en-it/womens-running-shoes/c/as20201000/?sz=96&start={}'],
        ['Туристические кросовки женские', 'Обувь женская', 3, 'https://www.asics.com/it/en-it/womens-trail-running-hiking-shoes/c/as20201010/?sz=96&start={}'],
        ['Теннисные кросовки женские', 'Обувь женская', 3, 'https://www.asics.com/it/en-it/womens-tennis-shoes/c/as20203000/?sz=96&start={}'],
        ['Волейбольные кросовки женские', 'Обувь женская', 3, 'https://www.asics.com/it/en-it/womens-volleyball-shoes/c/as20204000/?sz=96&start={}'],
        ['Гандбольные кросовки женские', 'Обувь женская', 3, 'https://www.asics.com/it/en-it/womens-handball-shoes/c/as20216000/?sz=96&start={}'],
        ['Падельные кросовки женские', 'Обувь женская', 3, 'https://www.asics.com/it/en-it/womens-padel-shoes/c/as20205000/?sz=96&start={}'],
        ['Нетбольные кросовки женские', 'Обувь женская', 3, 'https://www.asics.com/it/en-it/womens-netball-shoes/c/as20217000/?sz=96&start={}'],
        ['Повседневные кросовки женские', 'Обувь женская', 3, 'https://www.asics.com/it/en-it/sportstyle-women-shoes/c/as20220000/?sz=96&start={}'],
        
        ['Одежда женская', 'Женщины', 2],
        ['Спортивные бюстгальтеры женские', 'Одежда женская', 3, 'https://www.asics.com/it/en-it/sportstyle-women-shoes/c/as20220000/?sz=96&start={}'],
        ['Футболки без рукава женские', 'Одежда женская', 3, 'https://www.asics.com/it/en-it/womens-tank-tops/c/as20301010/?sz=96&start={}'],
        ['Футболки женские', 'Одежда женская', 3, 'https://www.asics.com/it/en-it/womens-short-sleeve-shirts/c/as20301040/?sz=96&start={}'],
        ['Лонгсливы женские', 'Одежда женская', 3, 'https://www.asics.com/it/en-it/womens-long-sleeve-shirts/c/as20301050/?sz=96&start={}'],
        ['Худи и свитшоты женские', 'Одежда женская', 3, 'https://www.asics.com/it/en-it/womens-hoodies-sweatshirts/c/as20301020/?sz=96&start={}'],
        ['Куртки женские', 'Одежда женская', 3, 'https://www.asics.com/it/en-it/womens-jackets-vests/c/as20301030/?sz=96&start={}'],
        ['Шорты женские', 'Одежда женская', 3, 'https://www.asics.com/it/en-it/womens-shorts/c/as20302020/?sz=96&start={}'],
        ['Штаны женские', 'Одежда женская', 3, 'https://www.asics.com/it/en-it/womens-pants/c/as20302030/?sz=96&start={}'],
        ['Леггинцы женские', 'Одежда женская', 3, 'https://www.asics.com/it/en-it/womens-tights-leggings/c/as20302010/?sz=96&start={}'],
        ['Юбки и платья женские', 'Одежда женская', 3, 'https://www.asics.com/it/en-it/womens-skirts-dresses/c/as20302040/?sz=96&start={}'],
        
        ['Аксессуары женские', 'Женщины', 2],
        ['Головные уборы женские', 'Аксессуары женские', 3, 'https://www.asics.com/it/en-it/as20401000/?sz=96&start={}'],
        ['Перчатки женские', 'Аксессуары женские', 3, 'https://www.asics.com/it/en-it/womens-gloves/c/as20405000/?sz=96&start={}'],
        ['Носки женские', 'Аксессуары женские', 3, 'https://www.asics.com/it/en-it/womens-socks/c/as20402000/?sz=96&start={}'],
        ['Сумки и рюкзаки женские', 'Аксессуары женские', 3, 'https://www.asics.com/it/en-it/womens-bags-packs/c/as20404000/?sz=96&start={}'],
        ['Экипировка женская', 'Аксессуары женские', 3, 'https://www.asics.com/it/en-it/womens-bags-packs/c/as20404000/?sz=96&start={}'],
        
        ['Дети'],
        ['Обувь детская', 'Дети', 2],
        ['Беговые кросовки детские', 'Обувь детская', 3, 'https://www.asics.com/it/en-it/kids-running-shoes/c/as30201000/?sz=96&start={}'],
        ['Теннисные кросовки детские', 'Обувь детская', 3, 'https://www.asics.com/it/en-it/kids-tennis-shoes/c/as30203000/?sz=96&start={}'],
        ['Другие кросовки детские', 'Обувь детская', 3, 'https://www.asics.com/it/en-it/kids-other-sports/c/as30219000/?sz=96&start={}'],
        ['Повседневные кросовки детские', 'Обувь детская', 3, 'https://www.asics.com/it/en-it/sportstyle-kids-shoes/c/as30220000/?sz=96&start={}'],
        
        ['Одежда детская', 'Дети', 2],
        ['Одежда детская (верх)', 'Одежда детская', 3, 'https://www.asics.com/it/en-it/kids-tops/c/as30301000/?sz=96&start={}'],
        ['Одежда детская (низ)', 'Одежда детская', 3, 'https://www.asics.com/it/en-it/kids-bottoms/c/as30302000/?sz=96&start={}'],

        ['Аутлет'],
        ['Мужчины аутлет', 'Аутлет', 2],
        ['Обувь мужская аутлет', 'Мужчины аутлет', 3],
        ['Беговые кросовки мужские аутлет', 'Обувь мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/mens-running-shoes/c/ao10201000/?sz=96&start={}'],
        ['Туристические кросовки мужские аутлет', 'Обувь мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/mens-trail/c/ao10209000/?sz=96&start={}'],
        ['Теннисные кросовки мужские аутлет', 'Обувь мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/mens-tennis-shoes/c/ao10202000/?sz=96&start={}'],
        ['Другие кросовки мужские аутлет', 'Обувь мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/ao10206000/?sz=96&start={}'],
        ['Повседневные кросовки мужские аутлет', 'Обувь мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/ao10205000/?sz=96&start={}'],

        ['Одежда мужская аутлет', 'Мужчины аутлет', 3],
        ['Футболки мужские аутлет', 'Одежда мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/mens-short-sleeve-shirts/c/ao10301000/?sz=96&start={}'],
        ['Лонгсливы мужские аутлет', 'Одежда мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/mens-long-sleeve-shirts/c/ao10302000/?sz=96&start={}'],
        ['Куртки мужские аутлет', 'Одежда мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/mens-jackets-vests/c/ao10307000/?sz=96&start={}'],
        ['Леггинцы мужские аутлет', 'Одежда мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/mens-tights-leggings/c/ao10304000/?sz=96&start={}'],
        ['Шорты мужские аутлет', 'Одежда мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/mens-shorts/c/ao10305000/?sz=96&start={}'],
        ['Штаны мужские аутлет', 'Одежда мужская аутлет', 4, 'https://outlet.asics.com/it/en-it/mens-pants/c/ao10306000/?sz=96&start={}'],
        
        ['Аксессуары мужские аутлет', 'Мужчины аутлет', 3],
        ['Сумки и рюкзаки мужские аутлет', 'Аксессуары мужские аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-bags-packs/c/ao20402000/?sz=96&start={}'],
        ['Головные уборы и перчатки мужские аутлет', 'Аксессуары мужские аутлет', 4, 'https://outlet.asics.com/it/en-it/hats-and-gloves/c/ao100000081/?sz=96&start={}'],
        ['Носки мужские аутлет', 'Аксессуары мужские аутлет', 4, 'https://outlet.asics.com/it/en-it/mens-socks/c/ao10401000/?sz=96&start={}'],

        ['Женщины аутлет', 'Аутлет', 2],
        ['Обувь женская аутлет', 'Женщины аутлет', 3],
        ['Беговые кросовки женские аутлет', 'Обувь женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-running-shoes/c/ao20201000/?sz=96&start={}'],
        ['Туристические кросовки женские аутлет', 'Обувь женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-trail/c/ao20208000/?sz=96&start={}'],
        ['Теннисные кросовки женские аутлет', 'Обувь женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-tennis-shoes/c/ao20202000/?sz=96&start={}'],
        ['Другие кросовки женские аутлет', 'Обувь женская аутлет', 4, 'https://outlet.asics.com/it/en-it/ao20203000/?sz=96&start={}'],
        ['Повседневные кросовки женские аутлет', 'Обувь женская аутлет', 4, 'https://outlet.asics.com/it/en-it/ao20205000/?sz=96&start={}'],
        
        ['Одежда женская аутлет', 'Женщины аутлет', 3],
        ['Спортивные бюстгальтеры женские аутлет', 'Одежда женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-sports-bras/c/ao20301000/?sz=96&start={}'],
        ['Футболки без рукава женские аутлет', 'Одежда женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-tank-tops/c/ao20304000/?sz=96&start={}'],
        ['Футболки женские аутлет', 'Одежда женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-short-sleeve-shirts/c/ao20302000/?sz=96&start={}'],
        ['Лонгсливы женские аутлет', 'Одежда женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-long-sleeve-shirts/c/ao20303000/?sz=96&start={}'],
        ['Куртки женские аутлет', 'Одежда женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-jackets-vests/c/ao20308000/?sz=96&start={}'],
        ['Шорты женские аутлет', 'Одежда женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-shorts/c/ao20306000/?sz=96&start={}'],
        ['Штаны женские аутлет', 'Одежда женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-pants/c/ao20307000/?sz=96&start={}'],
        ['Леггинцы женские аутлет', 'Одежда женская аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-tights-leggings/c/ao20305000/?sz=96&start={}'],
        
        ['Аксессуары женские аутлет', 'Женщины аутлет', 3],
        ['Сумки и рюкзаки женские аутлет', 'Аксессуары женские аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-bags-packs/c/ao20402000/?sz=96&start={}'],
        ['Головные уборы и перчатки женские аутлет', 'Аксессуары женские аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-hats-headbands-beanies/c/ao20403000/?sz=96&start={}'],
        ['Носки женские аутлет', 'Аксессуары женские аутлет', 4, 'https://outlet.asics.com/it/en-it/womens-socks/c/ao20401000/?sz=96&start={}'],
    ]
    cat_name = 'Asics'
    for subcategory in subcategories:
        if not str(subcategory[-1]).startswith('http'):
            if len(subcategory) == 1:
                crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            else:
                if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                    parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
                    crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue
    
        logging.info(f'Starting Asics: {subcategory[0]}')
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession(headers=headers, trust_env=True) as session:
            item_links = []
            for i in range(0, 10):
                await asyncio.sleep(5)
                async with session.get(subcategory[-1].format(96 * i), ssl=False) as response:
                    webpage = await response.read()
                    logging.info(f'Asics  {response.status}')
                    soup = bs(webpage, 'html.parser')
                    links = [link.find('a', 'product-tile__link js-product-tile').get('href') for link in soup.find_all('li', ['grid-tile new-row ', 'grid-tile'])]
                    if len(links) > 0:
                        item_links += links
                    else:
                        break

            items = []
            euro_costs = euro_cost()
            for item_url in item_links:
                try:
                    await asyncio.sleep(2)
                    async with session.get(item_url, ssl=False) as response:
                        item_wp = await response.read()
                        item_sp = bs(item_wp, 'html.parser')
                        title = item_sp.find('div', 'pdp-top__product-name large-bold').text.replace('\n', '').strip(' ')
                        #print(title)
                        color = item_sp.find_all('span', 'variants__header variants__header--light small-reg')[0].text
                        #print(color)
                        try:
                            old_price = int((float(item_sp.find('span', 'price-standard outlet-pricing').text.replace('\n', '').strip(' ').strip(' €').replace(',00', ' ').replace(',', '.')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Asics').margin}"))
                        except:
                            old_price = None
                        current_price = int((float(item_sp.find('span', 'price-sales price-sales-discount').text.replace('\n', '').strip(' ').strip(' €').replace(',00', ' ').replace(',', '.')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Asics').margin}"))
                        
                        percent = int(100 - float(current_price) / (float(old_price) / 100))
                        #print(old_price)
                        #print(current_price)
                        #print(percent)
                        description = ''
                        #description = item_sp.find('div', 'product-info-section-inner small-reg').text.strip('\n').replace('\n\n', '\n')
                        #print(description)
                        if old_price:
                            description = description[:700] + f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                        try:
                            sizes = ''
                            sizes_tag = item_sp.find('ul', 'variants__list variants__list--size js-mens-size').find_all('li')
                            for size in sizes_tag:
                                if size.get('data-instock') == 'true':
                                    sizes += size.text.replace('\n', '').strip(' ') + ', '
                            sizes = sizes.strip(', ')
                            description += '\n\nРазмеры:\n' + sizes
                            #print(sizes)
                        except:
                            pass
                        article = item_url.split('/')[-1].split('.')[0]
                        #print(article)

                        image_links = [a.get('href') for a in item_sp.find('div', 'product-thumbnails').find_all('a')]
                        # изображения
                        if not os.path.exists(f"database/images/{cat_name}"):
                            os.mkdir(f"database/images/{cat_name}")

                        if not os.path.exists(f"database/images/{cat_name}/{subcategory[0]}"):
                            os.mkdir(f"database/images/{cat_name}/{subcategory[0]}")

                        i = item_links.index(item_url) + 1
                        images = ''
                        
                        for url in image_links[:10]:
                            try:
                                num = image_links.index(url) + 1
                                img_path = f"database/images/{cat_name}/{subcategory[0]}/{i}_{title.replace(' ', '_').replace('/', '_')}_{num}.png"
                                if not os.path.exists(img_path):
                                    async with session.get(url, ssl=False) as response:
                                        f = await aiofiles.open(img_path, mode='wb')
                                        await f.write(await response.read())
                                        await f.close()
                                images +=  img_path + '\n'
                            except:
                                continue
                        items.append([title, description, current_price, images, sizes, article, item_url])
                        #logging.info([title, description, current_price, images, sizes, article, item_url])
                except Exception as ex:
                    logging.warning(f'{cat_name} pr - {ex}')
        # Добавление товаров
        if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
            crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        
        crud.create_products(category=cat_name, subcategory=subcategory[0], items=items)

        logging.info(f'Canceled {cat_name} {subcategory[0]} added {len(items)} products')
    await bot.send_message(227184505, f'{cat_name} закончил парсинг')


async def get_newbalance():
    subcategories = [
        ['Мужчины'],
        ['Обувь мужская', 'Мужчины', 2],
        ['Беговая обувь мужская', 'Обувь мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=101000&start={}&sz={}'],
        ['Кросовки мужские', 'Обувь мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=106000&start={}&sz={}'],
        ['Кросовки из США и Великобритании мужские', 'Обувь мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=107000&start={}&sz={}'],
        ['Кросовки для трейлранинга мужские', 'Обувь мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=13000&start={}&sz={}'],
        ['Сандалии мужские', 'Обувь мужская', 3, 'https://www.newbalance.it/it/sandali-uomo/'],
        ['Тренировочные кросовки мужские', 'Обувь мужская', 3, 'https://www.newbalance.it/it/uomo/scarpe/allenamento/'],
        ['Футбольные бутсы мужские', 'Обувь мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=73100&start={}&sz={}'],
        ['Кросовки для скейтбординга мужские', 'Обувь мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=108000&start={}&sz={}'],
        ['Теннисные мужские', 'Обувь мужская', 3, 'https://www.newbalance.it/it/tennis/scarpe/'],
        
        ['Одежда мужская', 'Мужчины', 2],
        ['Толстовки мужские', 'Одежда мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=159001&start={}&sz={}'],
        ['Штаны и леггинцы мужские', 'Одежда мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=158000&start={}&sz={}'],
        ['Куртки мужские', 'Одежда мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=157000&start={}&sz={}'],
        ['Футболки мужские', 'Одежда мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=155000&start={}&sz={}'],
        ['Шорты мужские', 'Одежда мужская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=153000&start={}&sz={}'],
        
        ['Аксессуары мужские', 'Мужчины', 2],
        ['Носки мужские', 'Аксессуары мужские', 3, 'https://www.newbalance.it/it/uomo/accessori/calzini/'],
        ['Сумки и рюкзаки мужские', 'Аксессуары мужские', 3, 'https://www.newbalance.it/it/men/clothing/accessories/bags-backpacks/'],
        ['Головные уборы мужские', 'Аксессуары мужские', 3, 'https://www.newbalance.it/it/uomo/accessori/berretti-e-cappelli/'],
        ['Спортивные аксессуары мужские', 'Аксессуары мужские', 3, 'https://www.newbalance.it/it/uomo/accessori/attrezzatura-sportiva/'],

        ['Женщины'],
        ['Обувь женская', 'Женщины', 2],
        ['Беговая обувь женская', 'Обувь женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=201000&start={}&sz={}'],
        ['Кросовки женские', 'Обувь женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=206000&start={}&sz={}'],
        ['Кросовки из США и Великобритании женские', 'Обувь женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=220000&start={}&sz={}'],
        ['Кросовки для трейлранинга женские', 'Обувь женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=202000&start={}&sz={}'],
        ['Сандалии женские', 'Обувь женская', 3, 'https://www.newbalance.it/it/sandali-donna/'],
        ['Тренировочные кросовки женские', 'Обувь женская', 3, 'https://www.newbalance.it/it/donna/scarpe/allenamento/'],
        ['Футбольные бутсы женские', 'Обувь женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=210000&start={}&sz={}'],
        ['Кросовки для скейтбординга женские', 'Обувь женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=108000&start={}&sz={}'],
        ['Теннисные женские', 'Обувь женская', 3, 'https://www.newbalance.it/it/tennis/scarpe/'],
        
        ['Одежда женская', 'Женщины', 2],
        ['Толстовки женские', 'Одежда женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=159001&start={}&sz={}'],
        ['Штаны и леггинцы женские', 'Одежда женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=158000&start={}&sz={}'],
        ['Куртки женские', 'Одежда женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=157000&start={}&sz={}'],
        ['Футболки женские', 'Одежда женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=155000&start={}&sz={}'],
        ['Шорты женские', 'Одежда женская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=153000&start={}&sz={}'],
        
        ['Дети'],
        ['Обувь детская', 'Дети', 2],
        ['Подростки (35,5 - 39 размер)', 'Обувь детская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=31001-1&start={}&sz={}'],
        ['Дети (28 - 35 размер)', 'Обувь детская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=31001-2&start={}&sz={}'],
        ['Младенцы (16 - 27,5 размер)', 'Обувь детская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=31001-3&start={}&sz={}'],
        ['Кросовки детские', 'Обувь детская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=31001-4&start={}&sz={}'],
        ['Беговые кросовки детские', 'Обувь детская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=31001-5&start={}&sz={}'],
        ['Футбольные бутсы детские', 'Обувь детская', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=39000-2&start={}&sz={}'],
        ['Сандалии детские', 'Обувь детская', 3, 'https://www.newbalance.it/it/bambino/scarpe/sandali/'],

        ['Одежда детская', 'Дети', 2, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=31002&start={}&sz={}'],
        
        ['Аутлет'],
        ['Мужчины', 'Аутлет', 2],
        ['Обувь мужская аутлет', 'Мужчины', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=50262-11&start={}&sz={}'],
        ['Одежда мужская аутлет', 'Мужчины', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=50262-12&start={}&sz={}'],
        ['Женщины', 'Аутлет', 2],
        ['Обувь женская аутлет', 'Женщины', 3, 'https://www.newbalance.it/it/outlet/donna/scarpe/'],
        ['Одежда женская аутлет', 'Женщины', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=50262-12&start={}&sz={}'],
        ['Дети', 'Аутлет', 2],
        ['Обувь детская аутлет', 'Дети', 3, 'https://www.newbalance.it/on/demandware.store/Sites-NBEU-Site/it_IT/Search-UpdateGrid?cgid=50262-33&start={}&sz={}'],
        ['Одежда детская аутлет', 'Дети', 3, 'https://www.newbalance.it/it/outlet/bambino/abbigliamento/'],
    ]
    cat_name = 'Newbalance'
    for subcategory in subcategories:
        if not str(subcategory[-1]).startswith('http'):
            if len(subcategory) == 1:
                crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            else:
                if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                    parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
                    crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue
        logging.info(f'Starting {cat_name}: {subcategory[0]}')
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession(headers=headers, trust_env=True) as session:
            for i in range(0, 1):
                async with session.get(subcategory[-1].format(0, 500), ssl=False) as response:
                    webpage = await response.read()
                    soup = bs(webpage, 'html.parser')
                    item_links = ['https://www.newbalance.it/' + item.find('a').get('href') for item in soup.find_all('div', 'image-container')]
            items = []
            euro_costs = euro_cost()
            for item_url in item_links:
                try:
                    await asyncio.sleep(2)
                    async with session.get(item_url, ssl=False) as response:
                        item_webpage = await response.read()
                        soup = bs(item_webpage, 'html.parser')
                        article = item_url.split('-')[-1].split('.')[0]
                        title = soup.find('h1', 'product-name hidden-sm-down').text
                        #print(title)
                        current_price = int((float(soup.find('span', 'sales font-body-large').text.strip('\r\n        ').strip('€').replace(',00', '').replace(',', '.')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Asics').margin}"))
                        #print(current_price)
                        try:
                            old_price = int((float(soup.find('span', 'strike-through list col-12 p-0 m-0 sales font-body-large').find('span', 'value').get('content')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Asics').margin}"))
                            percent = int(100 - float(current_price) / (float(old_price) / 100))
                        except:
                            old_price = None
                        #print(old_price)
                        #print(percent)
                        description = ''
                        
                        if old_price:
                            description = description[:700] + f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                        try:
                            size_list = ''
                            sizes = soup.find('div', 'select-attribute-grid attribute-grid-5').find_all('span')
                            for size in sizes:
                                if 'selectable' in size.get('class'):
                                    size_list += size.text.strip('\n').strip(' ').strip('\n').strip(' ') + ', '
                            size_list = size_list.strip(', ')
                            #print(size_list)
                            description += '\n\nРазмеры:\n' + size_list
                        except:
                            pass
                        #print(description)
                        image_links = [image.find('img').get('data-src') for image in soup.find('div', 'carousel-inner carousel-desktop').find_all('div', ['carousel-item zoom-image-js active', 'carousel-item zoom-image-js false'])]
                        # изображения
                        if not os.path.exists(f"database/images/{cat_name}"):
                            os.mkdir(f"database/images/{cat_name}")

                        if not os.path.exists(f"database/images/{cat_name}/{subcategory[0]}"):
                            os.mkdir(f"database/images/{cat_name}/{subcategory[0]}")

                        i = item_links.index(item_url) + 1
                        images = ''
                        
                        for url in image_links[:10]:
                            try:
                                num = image_links.index(url) + 1
                                img_path = f"database/images/{cat_name}/{subcategory[0]}/{i}_{title.replace(' ', '_').replace('/', '_')}_{num}.png"
                                if not os.path.exists(img_path):
                                    async with session.get(url, ssl=False) as response:
                                        f = await aiofiles.open(img_path, mode='wb')
                                        await f.write(await response.read())
                                        await f.close()
                                images +=  img_path + '\n'
                            except:
                                continue
                        items.append([title, description, current_price, images, size_list, article, item_url])
                except Exception as ex:
                    logging.warning(f'{cat_name} pr - {ex}')
        
        if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
            crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        
        crud.create_products(category=cat_name, subcategory=subcategory[0], items=items)

        logging.info(f'Canceled {cat_name} {subcategory[0]} added {len(items)} products') 
    await bot.send_message(227184505, f'{cat_name} закончил парсинг')


async def get_underarmour():
    cat_name = 'Underarmour'
    subcategories = [
        ['Мужчины'],
        ['Мужская одежда', 'Мужчины', 2],
        ['Мужская oдежда (верх)', 'Мужская одежда', 3, 'https://www.underarmour.it/en-it/c/mens/clothing/tops/?start=0&sz=1000'],
        ['Мужская одежда (низ)', 'Мужская одежда', 3, 'https://www.underarmour.it/en-it/c/mens/clothing/bottoms/?start=0&sz=1000'],
        ['Мужская обувь', 'Мужчины', 2],
        ['Мужская обувь', 'Мужчины', 3, 'https://www.underarmour.it/en-it/c/mens/shoes/?start=0&sz=1000'],
        ['Мужская верхняя одежда', 'Мужская одежда', 3, 'https://www.underarmour.it/en-it/c/mens/clothing/outerwear/?start=0&sz=1000'],
        ['Мужское белье', 'Мужская одежда', 3, 'https://www.underarmour.it/en-it/c/mens/clothing/underwear/?start=0&sz=1000'],
        ['Мужские спортивные костюмы', 'Мужская одежда', 3, 'https://www.underarmour.it/en-it/men-tracksuits/?start=0&sz=1000'],
        ['Женщины'],
        ['Женская одежда', 'Женщины', 2],
        ['Женская обувь', 'Женщины', 2],
        ['Женская одежда (верх)', 'Женская одежда', 3, 'https://www.underarmour.it/en-it/c/womens/clothing/tops/?start=0&sz=1000'],
        ['Женские бюстгальтеры', 'Женская одежда', 3, 'https://www.underarmour.it/en-it/c/womens/clothing/sports-bras/?start=0&sz=1000'],
        ['Женская одежда (низ)', 'Женская одежда', 3, 'https://www.underarmour.it/en-it/c/womens/clothing/bottoms/?start=0&sz=1000'],
        ['Женская верхняя одежда', 'Женская одежда', 3, 'https://www.underarmour.it/en-it/c/womens/clothing/outerwear/?start=0&sz=1000'],
        ['Женское белье', 'Женская одежда', 3, 'https://www.underarmour.it/en-it/c/womens/clothing-underwear/?start=0&sz=1000'],
        ['Женская обувь', 'Женщины', 3, 'https://www.underarmour.it/en-it/c/womens/shoes/?start=0&sz=1000'],
        ['Дети'],
        ['Мальчики', 'Дети', 2],
        ['Мальчики одежда', 'Мальчики', 3],
        ['Мальчики одежда (верх)', 'Мальчики одежда', 4, 'https://www.underarmour.it/en-it/c/boys/clothing/tops/?start=0&sz=1000'],
        ['Мальчики одежда (низ)', 'Мальчики одежда', 4, 'https://www.underarmour.it/en-it/c/boys/clothing/bottoms/?start=0&sz=1000'],
        ['Мальчики аксессуары', 'Мальчики одежда', 4, 'https://www.underarmour.it/en-it/c/boys/accessories/?start=0&sz=1000'],
        ['Мальчики спортивные костюмы', 'Мальчики одежда', 4, 'https://www.underarmour.it/en-it/c/boys/clothing/one-piece/?start=0&sz=1000'],
        ['Мальчики обувь', 'Мальчики', 3, 'https://www.underarmour.it/en-it/c/boys/shoes/?start=0&sz=1000'],
        ['Девочки', 'Дети', 2],
        ['Девочки одежда', 'Девочки', 3],
        ['Девочки одежда (верх)', 'Девочки одежда', 4, 'https://www.underarmour.it/en-it/c/girls/clothing/tops/?start=0&sz=1000'],
        ['Девочки одежда (низ)', 'Девочки одежда', 4, 'https://www.underarmour.it/en-it/c/girls/clothing/bottoms/?start=0&sz=1000'],
        ['Девочки аксессуары', 'Девочки одежда', 4, 'https://www.underarmour.it/en-it/c/girls/accessories/?start=0&sz=1000'],
        ['Девочки спортивные костюмы', 'Девочки одежда', 4, 'https://www.underarmour.it/en-it/c/girls/clothing/one-piece/?start=0&sz=1000'],
        ['Девочки бюстгальтеры', 'Девочки одежда', 4, 'https://www.underarmour.it/en-it/c/girls/clothing/sports-bras/?start=0&sz=1000'],
        ['Девочки обувь', 'Девочки', 3, 'https://www.underarmour.it/en-it/c/girls/shoes/?start=0&sz=1000'],

    ]
    for subcategory in subcategories:
        if not str(subcategory[-1]).startswith('http'):
            if len(subcategory) == 1:
                crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            else:
                if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                    parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
                    crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue
        logging.info(f'Starting {cat_name}: {subcategory[0]}')
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession(headers=headers, trust_env=True) as session:
            for i in range(0, 1):
                async with session.get(subcategory[-1], ssl=False) as response:
                    webpage = await response.text()
                    soup = bs(webpage, 'html.parser')
                    item_urls = [{'title' : item.text, 'url': 'https://www.underarmour.it' + item.get('href')} for item in soup.find_all('a', 'b-tile-name')]
            items = []
            euro_costs = euro_cost()
            for item_url in item_urls:
                try:
                    await asyncio.sleep(2)
                    async with session.get(item_url['url'], ssl=False) as response:
                        item_webpage = await response.read()
                        item_soup = bs(item_webpage, 'html.parser')
                        try:
                            current_price = int((float(item_soup.find('span', 'b-price-value highlighted bfx-price m-actual').text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Underarmour').margin}"))
                        except:
                            current_price = int((float(item_soup.find('span', 'b-price-value bfx-price').text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Underarmour').margin}"))

                        #print([current_price])
                        try:
                            old_price = int((float(item_soup.find('span', 'b-price-value m-strikethrough bfx-price highlighted').text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Underarmour').margin}"))
                            #print([old_price])
                            percent = int(100 - float(current_price) / (float(old_price) / 100))
                        except:
                            old_price = None
                        #description = item_soup.find('ul', 't-tabs_data').text.strip('\n')
                        description = ''
                        if old_price:
                            description = description[:700] + f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                        #print(description)
                        sizes = ''
                        try:
                            sizes_lst = [a.text.strip('\n') for a in item_soup.find('ul', 'js-input_field input-select form-control b-swatches_sizes').find_all('a')]
                            for size in sizes_lst:
                                sizes += size + ', '
                            sizes = sizes.strip(', ')
                            #print(sizes)
                            description += '\n\nРазмеры:\n' + sizes
                        except:
                            pass
                        image_links = [image.find('img').get('src') for image in item_soup.find_all('div', 'b-product_carousel-slide js-product_carousel-slide swiper-slide')]
                        #print(image_links)
                        # изображения
                        if not os.path.exists(f"database/images/{cat_name}"):
                            os.mkdir(f"database/images/{cat_name}")

                        if not os.path.exists(f"database/images/{cat_name}/{subcategory[0]}"):
                            os.mkdir(f"database/images/{cat_name}/{subcategory[0]}")

                        i = item_urls.index(item_url) + 1
                        images = ''
                        
                        for url in image_links[:10]:
                            try:
                                num = image_links.index(url) + 1
                                img_path = f"database/images/{cat_name}/{subcategory[0]}/{i}_{item_url['title'].replace(' ', '_').replace('/', '_')}_{num}.png"
                                if not os.path.exists(img_path):
                                    async with session.get(url, ssl=False) as response:
                                        f = await aiofiles.open(img_path, mode='wb')
                                        await f.write(await response.read())
                                        await f.close()
                                images +=  img_path + '\n'
                            except:
                                continue
                        article = item_url['url'].split('.html')[0].split('/')[-1] + '-' + item_url['url'].split('color=')[1].split('&')[0]
                        #print(article)
                        items.append([item_url['title'], description, current_price, images, sizes, article, item_url['url']])
                        #print([title, description, current_price, images, size_list, article, item_url])
                except Exception as ex:
                    logging.warning(f'{cat_name} pr - {ex}')
        
        if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
            crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        
        crud.create_products(category=cat_name, subcategory=subcategory[0], items=items)

        logging.info(f'Canceled {cat_name} {subcategory[0]} added {len(items)} products') 
    await bot.send_message(227184505, f'{cat_name} закончил парсинг')

async def get_pleinoutlet():
    cat_name = 'Philipp Plein Outlet'
    subcategories = [
        #https://www.pleinoutlet.com/it/en/search?cgid=men-clothing-leather&pmin=1.00&prefn1=hasPicture&prefv1=true&start=0&sz=1000
        ['Мужчины'],
        ['Мужская одежда', 'Мужчины', 2],
        ['Верхняя одежда мужская', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/jackets/?pmin=1.00&prefn1=hasPicture&prefv1=true&sz=150'],
        ['Кожаные куртки мужские', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/search?cgid=men-clothing-leather&pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Блейзеры мужские', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/blazers/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Трикотаж мужской', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/knitwear/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Поло мужские', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/polos/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Футболки мужские', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/t-shirts/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Рубашки мужские', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/shirts/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Беговая одежда мужская', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/sportswear/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Джинсы мужские', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/jeans/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Брюки и шорты мужские', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/search?cgid=men-clothing-trousers_and_shorts&pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Костюмы мужские', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/suits/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Нижнее белье мужское', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/underwear/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Пляжная одежда мужская', 'Мужская одежда', 3, 'https://www.pleinoutlet.com/it/en/men/clothing/beachwear/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'],
        ['Мужская обувь', 'Мужчины', 3],
        ['Кросовки мужские', 'Мужская обувь', 3, 'https://www.pleinoutlet.com/it/en/men/shoes/sneakers/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Сапоги мужские', 'Мужская обувь', 3, 'https://www.pleinoutlet.com/it/en/men/shoes/boots/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Туфли мужские', 'Мужская обувь', 3, 'https://www.pleinoutlet.com/it/en/men/shoes/classics/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Обувь на плоской подошве мужская', 'Мужская обувь', 3, 'https://www.pleinoutlet.com/it/en/men/shoes/flats/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Сандалии мужские', 'Мужская обувь', 3, 'https://www.pleinoutlet.com/it/en/men/shoes/sandals/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Мужские сумки', 'Мужчины', 2],
        ['Рюкзаки мужские', 'Мужские сумки', 3, 'https://www.pleinoutlet.com/it/en/men/bags/backpacks/'], 
        ['Наплечные сумки мужские', 'Мужские сумки', 3, 'https://www.pleinoutlet.com/it/en/men/bags/shoulder-bags/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Мешочки мужские', 'Мужские сумки', 3, 'https://www.pleinoutlet.com/it/en/men/bags/pouches/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Сумки для путешествий мужские', 'Мужские сумки', 3, 'https://www.pleinoutlet.com/it/en/men/bags/travel-bags/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Другие сумки мужские', 'Мужские сумки', 3, 'https://www.pleinoutlet.com/it/en/men/bags/other-bags/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Мужские аксессуары', 'Мужчины', 3],
        ['Ремни мужские', 'Мужские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/men/accessories/belts/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Очки мужские', 'Мужские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/men/accessories/eyewear/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Часы мужские', 'Мужские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/men/accessories/watches/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Небольшие кожаные изделия мужские', 'Мужские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/men/accessories/small-leather-goods/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Шляпы мужские', 'Мужские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/men/accessories/hats/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Шарфы мужские', 'Мужские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/men/accessories/scarves/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Брелки мужские', 'Мужские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/men/accessories/keychains/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Другие аксессуары мужские', 'Мужские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/men/accessories/other-accessories/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'],
        ['Женщины'],
        ['Женская одежда', 'Женщины', 2],
        ['Верхняя одежда женская', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/women/clothing/jackets/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Кожаные куртки женские', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/search?cgid=women-clothing-leather?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Блейзеры женские', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/women/clothing/blazers/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Платья и юбки женские', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/search?cgid=women-clothing-dresses_and_skirts?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Трикотаж женский', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/women/clothing/knitwear/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Футболки женские', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/women/clothing/t-shirts/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Топы женские', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/women/clothing/tops/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Одежда для бега женская', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/women/clothing/sportswear/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Джинсы женские', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/women/clothing/jeans/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'],
        ['Брюки и шорты женские', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/search?cgid=women-clothing-trousers_and_shorts&pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Костюмы женские', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/women/clothing/suits/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Пляжная одежда женская', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/women/clothing/beachwear/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Нижнее белье  женское', 'Женская одежда', 3, 'https://www.pleinoutlet.com/it/en/women/clothing/underwear/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Женская обувь', 'Женщины', 2],
        ['Кросовки женские', 'Женская обувь', 3, 'https://www.pleinoutlet.com/it/en/women/shoes/sneakers/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Сапоги женские', 'Женская обувь', 3, 'https://www.pleinoutlet.com/it/en/women/shoes/boots/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Туфли на высоком каблуке', 'Женская обувь', 3, 'https://www.pleinoutlet.com/it/en/women/shoes/pumps/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Туфли женские', 'Женская обувь', 3, 'https://www.pleinoutlet.com/it/en/women/shoes/classics/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Обувь на плоской подошве женская', 'Женская обувь', 3, 'https://www.pleinoutlet.com/it/en/women/shoes/flats/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Сандалии женские', 'Женская обувь', 3, 'https://www.pleinoutlet.com/it/en/women/shoes/sandals/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Женские сумки', 'Женщины', 2],
        ['Клачи женские', 'Женские сумки', 3, 'https://www.pleinoutlet.com/it/en/women/bags/clutches/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Сумки женские', 'Женские сумки', 3, 'https://www.pleinoutlet.com/it/en/women/bags/tote-bags/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Наплечные сумки женские', 'Женские сумки', 3, 'https://www.pleinoutlet.com/it/en/women/bags/shoulder-bags/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Рюкзаки женские', 'Женские сумки', 3, 'https://www.pleinoutlet.com/it/en/women/bags/backpacks/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Портфели женские', 'Женские сумки', 3, 'https://www.pleinoutlet.com/it/en/women/bags/pouches-and-portfolios/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Другие женские сумки', 'Женские сумки', 3, 'https://www.pleinoutlet.com/it/en/women/bags/other-bags/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Женские аксессуары', 'Женщины', 2],
        ['Ремни женские', 'Женские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/women/accessories/belts/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Очки женские', 'Женские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/women/accessories/eyewear/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Ювелирные украшения женские', 'Женские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/women/accessories/jewelry/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Небольшие кожаные изделия женские', 'Женские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/women/accessories/small-leather-goods/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Шляпы женские', 'Женские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/women/accessories/hats-/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Шарфы женские', 'Женские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/women/accessories/scarves/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Перчатки женские', 'Женские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/women/accessories/gloves/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Брелки женские', 'Женские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/women/accessories/keychains/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Другие женские аксессуары', 'Женские аксессуары', 3, 'https://www.pleinoutlet.com/it/en/women/accessories/other-accessories/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'],
        ['Дети'],
        ['Мальчики', 'Дети', 2],
        ['Одежда для мальчиков', 'Мальчики', 3, 'https://www.pleinoutlet.com/it/en/kids/boys/clothing/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Обувь для мальчиков', 'Мальчики', 3, 'https://www.pleinoutlet.com/it/en/kids/boys/shoes/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Аксессуары для мальчиков', 'Мальчики', 3, 'https://www.pleinoutlet.com/it/en/kids/boys/accessories/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'],
        ['Для младенцев мальчиков', 'Мальчики', 3, 'https://www.pleinoutlet.com/it/en/search?cgid=kids-boys-baby?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Девочки', 'Дети', 2],
        ['Одежда для девочек', 'Девочки', 3, 'https://www.pleinoutlet.com/it/en/kids/girls/clothing/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Обувь для девочек', 'Девочки', 3, 'https://www.pleinoutlet.com/it/en/kids/girls/shoes/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Аксессуары для девочек', 'Девочки', 3, 'https://www.pleinoutlet.com/it/en/kids/girls/accessories/?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax'], 
        ['Для младенцев девочек', 'Девочки', 3, 'https://www.pleinoutlet.com/it/en/search?cgid=kids-girls-baby?pmin=1.00&prefn1=hasPicture&prefv1=true&start={}&sz=100&format=ajax']
    ]
    
    for subcategory in subcategories:
        if not str(subcategory[-1]).startswith('http'):
            if len(subcategory) == 1:
                crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            else:
                if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                    parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
                    crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue
        logging.info(f'Starting {cat_name}: {subcategory[0]}')
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession(headers=headers, trust_env=True) as session:
            items_urls = []
            for i in range(0, 10):
                async with session.get(subcategory[-1].format(i * 20), ssl=False) as response:
                    webpage = await response.text()
                    soup = bs(webpage, 'html.parser')
                    page_items = [{'title': a.get('title'), 'url': 'https://www.pleinoutlet.com' + a.get('href')} for a in soup.find_all('a', 'b-product_tile-link')]
                    if len(page_items) > 0:    
                        items_urls += page_items
                    else:
                        continue
            items = []
            euro_costs = euro_cost()
            for item in items_urls:
                async with session.get(item['url'], ssl=False) as response:
                    try:
                        item_webpage = await response.read()
                        item_soup = bs(item_webpage, 'html.parser')
                        article = item['url'].split('.html')[0].split('/')[-1]
                        #print(article)
                        
                        current_price = int((float(item_soup.find('span', 'price-sales').text.strip('€ ').replace('.', '')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Philipp Plein Outlet').margin}"))
                        #print(current_price)
                        try:
                            old_price = int((float(item_soup.find('span', 'price-standard').text.strip('€ ').replace('.', '')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Philipp Plein Outlet').margin}"))
                            percent = int(100 - float(current_price) / (float(old_price) / 100))
                            description = f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                            #print(description)
                        except:
                            pass
                        try:
                            sizes = ''
                            for size in [li.text.strip('\n') for li in item_soup.find_all('li', 'b-swatches-item selectable variation-group-value')]:
                                sizes += size.replace('Last 1 left', '').replace('\n', '').strip(' ') + ', '
                            sizes = sizes.strip(', ')
                            description += '\n\nРазмеры:\n' + sizes
                            #print([sizes])
                        except:
                            pass
                        #print([sizes])
                        image_links = [img.get('src') for img in item_soup.find('div', 'b-pdp-thumbnails').find_all('img')]
                        #print(image_links)
                        # изображения
                        if not os.path.exists(f"database/images/{cat_name}"):
                            os.mkdir(f"database/images/{cat_name}")

                        if not os.path.exists(f"database/images/{cat_name}/{subcategory[0]}"):
                            os.mkdir(f"database/images/{cat_name}/{subcategory[0]}")

                        i = items_urls.index(item) + 1
                        images = ''
                        
                        for url in image_links[:10]:
                            try:
                                num = image_links.index(url) + 1
                                img_path = f"database/images/{cat_name}/{subcategory[0]}/{i}_{item['title'].replace(' ', '_').replace('/', '_')}_{num}.png"
                                if not os.path.exists(img_path):
                                    async with session.get(url, ssl=False) as response:
                                        f = await aiofiles.open(img_path, mode='wb')
                                        await f.write(await response.read())
                                        await f.close()
                                images +=  img_path + '\n'
                            except:
                                continue
                        items.append([item['title'], description, current_price, images, sizes, article, item['url']])
                    except Exception as ex:
                        print(ex)
                        
        if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
            crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        
        crud.create_products(category=cat_name, subcategory=subcategory[0], items=items)

        logging.info(f'Canceled {cat_name} {subcategory[0]} added {len(items)} products') 
    await bot.send_message(227184505, f'{cat_name} закончил парсинг')


async def get_monnalisa():
    cat_name = 'Monnalisa'
    subcategories = [
        #
        ['Девочки'],
        ['Девочки (0-18 месяцев)', 'Девочки', 2],
        ['Одежда для девочек (0-18 месяцев)', 'Девочки (0-18 месяцев)', 3],
        ['Платья и комбинезоны для девочек (0-18 месяцев)', 'Одежда для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/clothing/dresses-jumpsuits/?sz=1000'],
        ['Пляжная одежда для девочек (0-18 месяцев)', 'Одежда для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/clothing/beachwear/?sz=1000'],
        ['Пальто и куртки для девочек (0-18 месяцев)', 'Одежда для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/clothing/coats-jackets/?sz=1000'],
        ['Юбки для девочек (0-18 месяцев)', 'Одежда для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/clothing/skirts/?sz=1000'],
        ['Штаны и легинцы для девочек (0-18 месяцев)', 'Одежда для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/clothing/leggings-pants/?sz=1000'],
        ['Свитеры и кардигары для девочек (0-18 месяцев)', 'Одежда для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/clothing/cardigans-sweaters/?sz=1000'],
        ['Рубашки и футболки для девочек (0-18 месяцев)', 'Одежда для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/clothing/tops--t-shirts-shirts/?sz=1000'],
        ['Аксессуары для девочек (0-18 месяцев)', 'Девочки (0-18 месяцев)', 3, 'https://www.monnalisa.com/en-it/girl/0-18-months/accessories/?sz=1000'],
        ['Косметика для девочек (0-18 месяцев)', 'Девочки (0-18 месяцев)', 3, 'https://www.monnalisa.com/en-it/girl/0-18-months/beauty-skin/?sz=1000'],
        ['Обувь для девочек (0-18 месяцев)', 'Девочки (0-18 месяцев)', 3],
        ['Pre-Walker shoes девочки (0-18 месяцев)', 'Обувь для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/shoes/pre-walker-shoes/?sz=1000'],
        ['Балетки для девочек (0-18 месяцев)', 'Обувь для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/shoes/ballerinas/?sz=1000'],
        ['Сандалии для девочек (0-18 месяцев)', 'Обувь для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/shoes/sandals/?sz=1000'],
        ['Кросовки для девочек (0-18 месяцев)', 'Обувь для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/shoes/sneakers/?sz=1000'],
        ['Сапоги для девочек (0-18 месяцев)', 'Обувь для девочек (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/shoes/boots/?sz=1000'],
        
        ['Новорожденные девочки', 'Девочки (0-18 месяцев)', 3],
        ['Аксессуары для новорожденых девочек', 'Новорожденные девочки', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/newborn/baby-accessories/?sz=1000'],
        ['Боди и комбинезоны для новорожденых девочек', 'Новорожденные девочки', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/newborn/bodyvests--rompers-baby-sets/?sz=1000'],
        ['Постельные принадлежности для новорожденых девочек', 'Новорожденные девочки', 4, 'https://www.monnalisa.com/en-it/girl/0-18-months/newborn/bedding/?sz=1000'],
        
        #
        ['Девочки (2-12 лет)', 'Девочки', 2],
        ['Одежда для девочек (2-12 лет)', 'Девочки (2-12 лет)', 3],
        ['Платья и комбинезоны для девочек (2-12 лет)', 'Одежда для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/clothing/dresses-jumpsuits/?sz=1000'],
        ['Пляжная одежда для девочек (2-12 лет)', 'Одежда для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/clothing/beachwear/?sz=1000'],
        ['Пальто и куртки для девочек (2-12 лет)', 'Одежда для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/clothing/coats-jackets/?sz=1000'],
        ['Юбки для девочек (2-12 лет)', 'Одежда для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/clothing/skirts/?sz=1000'],
        ['Штаны и легинцы для девочек (2-12 лет)', 'Одежда для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/clothing/leggings-pants/?sz=1000'],
        ['Свитеры и кардигары для девочек (2-12 лет)', 'Одежда для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/clothing/cardigans-sweaters/?sz=1000'],
        ['Рубашки и футболки для девочек (2-12 лет)', 'Одежда для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/clothing/tops--t-shirts-shirts/?sz=1000'],
        
        ['Аксессуары для девочек (2-12 лет)', 'Девочки (2-12 лет)', 3, 'https://www.monnalisa.com/en-it/girl/2-12-years/accessories/?sz=1000'],
        ['Косметика для девочек (2-12 лет)', 'Девочки (2-12 лет)', 3, 'https://www.monnalisa.com/en-it/girl/2-12-years/beauty-skin/?sz=1000'],
        
        ['Обувь для девочек (2-12 лет)', 'Девочки (2-12 лет)', 3],
        ['Балетки для девочек (2-12 лет)', 'Обувь для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/shoes/ballerinas/?sz=1000'],
        ['Сандалии для девочек (2-12 лет)', 'Обувь для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/shoes/sandals/?sz=1000'],
        ['Кросовки для девочек (2-12 лет)', 'Обувь для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/shoes/sneakers/?sz=1000'],
        ['Сапоги для девочек (2-12 лет)', 'Обувь для девочек (2-12 лет)', 4, 'https://www.monnalisa.com/en-it/girl/2-12-years/shoes/boots/?sz=1000'],
        
        #
        ['Девочки (13-16 лет)', 'Девочки', 2],
        ['Одежда для девочек (13-16 лет)', 'Девочки (13-16 лет)', 3],
        ['Платья и комбинезоны для девочек (13-16 лет)', 'Одежда для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/clothing/dresses-jumpsuits/?sz=1000'],
        ['Пляжная одежда для девочек (13-16 лет)', 'Одежда для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/clothing/beachwear/?sz=1000'],
        ['Пальто и куртки для девочек (13-16 лет)', 'Одежда для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/clothing/coats-jackets/?sz=1000'],
        ['Юбки для девочек (13-16 лет)', 'Одежда для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/clothing/skirts/?sz=1000'],
        ['Штаны и легинцы для девочек (13-16 лет)', 'Одежда для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/clothing/leggings-pants/?sz=1000'],
        ['Свитеры и кардигары для девочек (13-16 лет)', 'Одежда для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/clothing/cardigans-sweaters/?sz=1000'],
        ['Рубашки и футболки для девочек (13-16 лет)', 'Одежда для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/clothing/tops--t-shirts-shirts/?sz=1000'],
        
        ['Аксессуары для девочек (13-16 лет)', 'Девочки (13-16 лет)', 3, 'https://www.monnalisa.com/en-it/girl/13-16-years/accessories/?sz=1000'],
        ['Косметика для девочек (13-16 лет)', 'Девочки (13-16 лет)', 3, 'https://www.monnalisa.com/en-it/girl/13-16-years/beauty-skin/'],
        
        ['Обувь для девочек (13-16 лет)', 'Девочки (13-16 лет)', 3],
        ['Балетки для девочек (13-16 лет)', 'Обувь для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/shoes/ballerinas/?sz=1000'],
        ['Сандалии для девочек (13-16 лет)', 'Обувь для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/shoes/sandals/?sz=1000'],
        ['Кросовки для девочек (13-16 лет)', 'Обувь для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/shoes/sneakers/?sz=1000'],
        ['Сапоги для девочек (13-16 лет)', 'Обувь для девочек (13-16 лет)', 4, 'https://www.monnalisa.com/en-it/girl/13-16-years/shoes/boots/?sz=1000'],
        
        #
        ['Мальчики'],
        ['Мальчики (0-18 месяцев)', 'Мальчики', 2],
        ['Одежда для мальчиков (0-18 месяцев)', 'Мальчики (0-18 месяцев)', 3],
        ['Пляжная одежда для мальчиков (0-18 месяцев)', 'Одежда для мальчиков (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/clothing/beachwear/?sz=1000'],
        ['Пальто и куртки для мальчиков (0-18 месяцев)', 'Одежда для мальчиков (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/clothing/coats-jackets/?sz=1000'],
        ['Штаны для мальчиков (0-18 месяцев)', 'Одежда для мальчиков (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/clothing/pants/?sz=1000'],
        ['Свитеры и кардигары для мальчиков (0-18 месяцев)', 'Одежда для мальчиков (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/clothing/cardigans-sweaters/?sz=1000'],
        ['Рубашки и футболки для мальчиков (0-18 месяцев)', 'Одежда для мальчиков (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/clothing/t-shirts-shirts/?sz=1000'],
        
        ['Аксессуары для мальчиков (0-18 месяцев)', 'Мальчики (0-18 месяцев)', 3, 'https://www.monnalisa.com/en-it/boy/0-18-months/accessories/?sz=1000'],
        ['Косметика для мальчиков (0-18 месяцев)', 'Мальчики (0-18 месяцев)', 3, 'https://www.monnalisa.com/en-it/boy/0-18-months/beauty-skin/?sz=1000'],
        ['Обувь для мальчиков (0-18 месяцев)', 'Мальчики (0-18 месяцев)', 3],
        ['Pre-Walker shoes мальчики (0-18 месяцев)', 'Обувь для мальчиков (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/shoes/pre-walker-shoes/?sz=1000'],
        ['Сандалии для мальчиков (0-18 месяцев)', 'Обувь для мальчиков (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/shoes/sandals/?sz=1000'],
        ['Кросовки для мальчиков (0-18 месяцев)', 'Обувь для мальчиков (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/shoes/sneakers/?sz=1000'],
        ['Сапоги для мальчиков (0-18 месяцев)', 'Обувь для мальчиков (0-18 месяцев)', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/shoes/boots/?sz=1000'],
        
        ['Новорожденные мальчики', 'Мальчики (0-18 месяцев)', 3],
        ['Аксессуары для новорожденых мальчиков', 'Новорожденные мальчики', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/newborn/baby-accessories/?sz=1000'],
        ['Боди и комбинезоны для новорожденых мальчиков', 'Новорожденные мальчики', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/newborn/bodyvests--rompers-baby-sets/?sz=1000'],
        ['Постельные принадлежности для новорожденых мальчиков', 'Новорожденные мальчики', 4, 'https://www.monnalisa.com/en-it/boy/0-18-months/newborn/bedding/?sz=1000'],
        
        #
        ['Мальчики (2-14 лет)', 'Мальчики', 2],
        ['Одежда для мальчиков (2-14 лет)', 'Мальчики (2-14 лет)', 3],
        ['Пляжная одежда для мальчиков (2-14 лет)', 'Одежда для мальчиков (2-14 лет)', 4, 'https://www.monnalisa.com/en-it/boy/2-14-years/clothing/beachwear/?sz=1000'],
        ['Пальто и куртки для мальчиков (2-14 лет)', 'Одежда для мальчиков (2-14 лет)', 4, 'https://www.monnalisa.com/en-it/boy/2-14-years/clothing/coats-jackets/?sz=1000'],
        ['Штаны для мальчиков (2-14 лет)', 'Одежда для мальчиков (2-14 лет)', 4, 'https://www.monnalisa.com/en-it/boy/2-14-years/clothing/pants/?sz=1000'],
        ['Свитеры и кардигары для мальчиков (2-14 лет)', 'Одежда для мальчиков (2-14 лет)', 4, 'https://www.monnalisa.com/en-it/boy/2-14-years/clothing/cardigans-sweaters/?sz=1000'],
        ['Рубашки и футболки для мальчиков (2-14 лет)', 'Одежда для мальчиков (2-14 лет)', 4, 'https://www.monnalisa.com/en-it/boy/2-14-years/clothing/tops--t-shirts-shirts/?sz=1000'],
        
        ['Аксессуары для мальчиков (2-14 лет)', 'Мальчики (2-14 лет)', 3, 'https://www.monnalisa.com/en-it/boy/2-14-years/accessories/?sz=1000'],
        ['Косметика для мальчиков (2-14 лет)', 'Мальчики (2-14 лет)', 3, 'https://www.monnalisa.com/en-it/boy/2-14-years/beauty-skin/?sz=1000'],
        
        ['Обувь для мальчиков (2-14 лет)', 'Мальчики (2-14 лет)', 3],
        ['Сандалии для мальчиков (2-14 лет)', 'Обувь для мальчиков (2-14 лет)', 4, 'https://www.monnalisa.com/en-it/boy/2-14-years/shoes/sandals/?sz=1000'],
        ['Кросовки для мальчиков (2-14 лет)', 'Обувь для мальчиков (2-14 лет)', 4, 'https://www.monnalisa.com/en-it/boy/2-14-years/shoes/sneakers/?sz=1000'],
        ['Сапоги для мальчиков (2-14 лет)', 'Обувь для мальчиков (2-14 лет)', 4, 'https://www.monnalisa.com/en-it/boy/2-14-years/shoes/boots/?sz=1000'],
        
        #
        ['Аутлет'],
        ['Девочки аутлет', 'Аутлет', 2],
        ['Одежда для девочек аутлет', 'Девочки аутлет', 3],
        ['Платья и комбинезоны для девочек аутлет', 'Одежда для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/dresses-jumpsuits/?sz=1000'],
        ['Пляжная одежда для девочек аутлет', 'Одежда для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/beachwear/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Пальто и куртки для девочек аутлет', 'Одежда для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/coats-jackets/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Кардиганы и свитеры для девочек аутлет', 'Одежда для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/cardigans-sweaters/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Футболки и рубашки для девочек аутлет', 'Одежда для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/tops--t-shirts-shirts/?sz=1000'],
        ['Юбки аутлет', 'Одежда для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/skirts/?sz=1000'],
        ['Штаны и леггинсы аутлет', 'Одежда для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/leggings-pants/?sz=1000'],
        
        ['Аксессуары для девочек аутлет', 'Девочки аутлет', 3],
        ['Аксессуары для волос аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/hair-accessories/?sz=1000'],
        ['Шляпы для девочек аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/hats/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Солнечные очки для девочек аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/sunglasses/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Ювелирные украшения для девочек аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/jewelry/?sz=1000'],
        ['Сумки и рюкзаки для девочек аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/bags-backpacks/?sz=1000'],
        ['Шарфы для девочек аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/scarves-foulards/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Перчатки для девочек аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/gloves/?sz=1000'],
        ['Фэшн для девочек аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/fashion-extra/?sz=1000'],
        ['Ремни для девочек аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/girl/accessories/belts/?sz=1000'],
        ['Носки для девочек аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/socks/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Носки и колготки для девочек аутлет', 'Аксессуары для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/socks-tights/?sz=1000'],

        ['Обувь для девочек аутлет', 'Девочки аутлет', 3],
        ['Pre-Walker shoes для девочек аутлет', 'Обувь для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/shoes/pre-walker-shoes/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Балетки для девочек аутлет', 'Обувь для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/girl/shoes/ballerinas/?sz=1000'],
        ['Шлепки для девочек аутлет', 'Обувь для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/shoes/slides/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Сандалии для девочек аутлет', 'Обувь для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/shoes/sandals/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Кросовки для девочек аутлет', 'Обувь для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/shoes/sneakers/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Сапоги для девочек аутлет', 'Обувь для девочек аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/shoes/boots/?prefn1=gender&prefv1=Girl&sz=1000'],
        
        ['Новорожденные девочки аутлет', 'Девочки аутлет', 3],
        ['Аксессуары для новорожденных девочек аутлет', 'Новорожденные девочки аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/newborn/baby-accessories/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Боди и комбинезоны для новорожденных девочек аутлет', 'Новорожденные девочки аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/newborn/bodyvests--rompers-baby-sets/?prefn1=gender&prefv1=Girl&sz=1000'],
        ['Постельное белье для новорожденных девочек аутлет', 'Новорожденные девочки аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/newborn/bedding/?prefn1=gender&prefv1=Girl&sz=1000'],

        ['Мальчики аутлет', 'Аутлет', 2],
        ['Одежда для мальчиков аутлет', 'Мальчики аутлет', 3],
        ['Пляжная одежда для мальчиков аутлет', 'Одежда для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/beachwear/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Пальто и куртки для мальчиков аутлет', 'Одежда для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/coats-jackets/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Кардиганы и свитеры для мальчиков аутлет', 'Одежда для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/cardigans-sweaters/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Футболки и рубашки для мальчиков аутлет', 'Одежда для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/t-shirts-shirts/?sz=1000'],
        ['Штаны аутлет', 'Одежда для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/clothing/pants/'],
        
        ['Аксессуары для мальчиков аутлет', 'Мальчики аутлет', 3],
        ['Шляпы для мальчиков аутлет', 'Аксессуары для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/hats/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Солнечные очки для мальчиков аутлет', 'Аксессуары для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/sunglasses/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Шарфы для мальчиков аутлет', 'Аксессуары для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/scarves-foulards/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Рюкзаки для мальчиков аутлет', 'Аксессуары для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/backpacks/?sz=1000'],
        ['Носки для мальчиков аутлет', 'Аксессуары для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/accessories/socks/?prefn1=gender&prefv1=Boy&sz=1000'],

        ['Обувь для мальчиков аутлет', 'Мальчики аутлет', 3],
        ['Pre-Walker shoes для мальчиков аутлет', 'Обувь для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/shoes/pre-walker-shoes/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Шлепки для мальчиков аутлет', 'Обувь для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/shoes/slides/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Сандалии для мальчиков аутлет', 'Обувь для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/shoes/sandals/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Кросовки для мальчиков аутлет', 'Обувь для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/shoes/sneakers/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Сапоги для мальчиков аутлет', 'Обувь для мальчиков аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/shoes/boots/?prefn1=gender&prefv1=Boy&sz=1000'],

        ['Новорожденные мальчики аутлет', 'Мальчики аутлет', 3],
        ['Аксессуары для новорожденных мальчиков аутлет', 'Новорожденные мальчики аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/newborn/baby-accessories/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Боди и комбинезоны для новорожденных мальчиков аутлет', 'Новорожденные мальчики аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/newborn/bodyvests--rompers-baby-sets/?prefn1=gender&prefv1=Boy&sz=1000'],
        ['Постельное белье для новорожденных мальчиков аутлет', 'Новорожденные мальчики аутлет', 4, 'https://www.monnalisa.com/en-it/outlet/newborn/bedding/?prefn1=gender&prefv1=Boy&sz=1000'],
    ]
    for subcategory in subcategories[:4]:
        if not str(subcategory[-1]).startswith('http'):
            if len(subcategory) == 1:
                crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            else:
                if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                    parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
                    crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue

        logging.info(f'Starting {cat_name}: {subcategory[0]}')
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession(headers=headers, trust_env=True) as session:
            #items_urls = []
            for i in range(0, 1):
                async with session.get(subcategory[-1], ssl=False) as response:
                    webpage = await response.text()
                    soup = bs(webpage, 'html.parser')
                    items_urls = [{'title': a.get('title'), 'url': 'https://www.monnalisa.com' + a.get('href')} for a in soup.find_all('a', 'link larger')]
            #for item in items_urls:
            #    print(item)
            items = []
            euro_costs = euro_cost()
            for item in items_urls[:5]:
                # item['url']
                async with session.get(item['url'], ssl=False) as response:
                    item_webpage = await response.text()
                    item_soup = bs(item_webpage, 'html.parser')

                    #print(item['title'])
                    current_price = int((float(item_soup.find('div', 'col-12 prices pt-0 pt-lg-2 order-1 order-lg-0').find('div', 'sales extra-large').text.strip('\n').replace('€ ', '').replace(',', '.')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Monnalisa').margin}"))
                    
                    #print([current_price])
                    description = ''
                    try:
                        old_price = int((float(item_soup.find('div', 'col-12 prices pt-0 pt-lg-2 order-1 order-lg-0').find('span', 'value small').get('content').replace(',', '.')) * (euro_costs + 1)) * float(f"1.{crud.get_category(name='Monnalisa').margin}"))
                        percent = int(100 - float(current_price) / (float(old_price) / 100))
                        description = f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                        
                    except:
                        pass
                    try:
                        sizes_list = [size.text.strip('\n').strip(' ').strip('\n') for size in item_soup.find('div', 'col-12 col-lg-7').find_all('option')[1:] if size.get('disabled') == None]
                        sizes = ''
                        for size in sizes_list:
                            sizes += size + ', '
                        sizes = sizes.strip(', ')
                        description += '\n\nРазмеры:\n' + sizes
                    except:
                        pass
                    #print(description)
                    article = item['url'].split('-')[-1].strip('.html')
                    #print(article)

                    image_links = [img.find('img').get('data-src') for img in item_soup.find('div', 'row gallery-container').find_all('div', 'image-container')][:]
                    #print(image_links)
                    # изображения
                    if not os.path.exists(f"database/images/{cat_name}"):
                        os.mkdir(f"database/images/{cat_name}")

                    if not os.path.exists(f"database/images/{cat_name}/{subcategory[0]}"):
                        os.mkdir(f"database/images/{cat_name}/{subcategory[0]}")

                    i = items_urls.index(item) + 1
                    images = ''
                    
                    for url in image_links[:10]:
                        try:
                            num = image_links.index(url) + 1
                            img_path = f"database/images/{cat_name}/{subcategory[0]}/{i}_{item['title'].replace(' ', '_').replace('/', '_')}_{num}.png"
                            if not os.path.exists(img_path):
                                async with session.get(url, ssl=False) as response:
                                    f = await aiofiles.open(img_path, mode='wb')
                                    await f.write(await response.read())
                                    await f.close()
                            images +=  img_path + '\n'
                        except:
                            continue
                    title = item['title'].replace('<br>', ' ')
                    items.append([title, description, current_price, images, sizes, article, item['url']])
                        
        if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=cat_name).id)
            crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        
        crud.create_products(category=cat_name, subcategory=subcategory[0], items=items)

        logging.info(f'Canceled {cat_name} {subcategory[0]} added {len(items)} products') 
    await bot.send_message(227184505, f'{cat_name} закончил парсинг')