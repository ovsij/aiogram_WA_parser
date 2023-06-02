import asyncio
import aiohttp
import aiofiles
import logging
from bs4 import BeautifulSoup as bs
import os
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

from database.db import *
from database import crud


EURO_COSTS = 87

cat_name = "Zwilling"
SUBCATEGORIES = [
    ["Посуда"],
    ["Воки", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/woks/"],
    ["Фондю", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/fondue/"],
    ["Крышки для посуды", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/coperchi/"],
    # ["Наборы кастрюль", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/set-di-pentole-da-cucina/"],
    # ["Наборы сковородок", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/set-di-padelle/"],
    # ["Ковши и жаровни", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/casseruole-con-manico/"],
    # ["Сковороды", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/padelle/"],
    # ["Сковороды-гриль", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/bistecchiere-e-griglie/"],
    # ["Сотейники", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/tegami/"],
    # ["Чайники", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/teiere/"],
    # ["Чугунные кокоты", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/cocottes/"],
    # ["Ручки для посуды", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/accessori/"],
    # ["Миски, рамекины", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/colapasta-e-cestelli/"],
    # ["Формы для запекания", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/cocottes/"],
    # ["Посуда специальной формы", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/speciali/"],
    # ["Блинница", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/crepiere/"],
    # ["Подставка", "Посуда", 2, "https://www.zwilling.com/it/pentole-e-padelle/sottopentole/"],

    # ["Кухонная утварь"],
    # ["Кухонные ножницы", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/forbici-da-cucina/"],
    # ["Ножницы для птицы", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/trinciapolli/"],
    # ["Терки", "Кухонная утварь", 2, "https://www.zwilling.com/it/z-cut/"],
    # ["Винные аксессуары", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/accessori-per-il-vino/"],
    # ["Банки", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/barattoli/"],
    # ["Хранение кухонной утвари", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/portautensili-da-cucina/"],
    # ["Практические инструменты", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/utensili-pratici/"],
    # ["Очистители картошки", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/pelapatate/"],
    # ["Шпатели", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/spatole-2/"],
    # ["Половники", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/mestoli/"],
    # ["Шумовки", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/schiumarole/"],
    # ["Лопатки", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/palette/"],
    # ["Венчики", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/fruste/"],
    # ["Кухонные полотенца", "Кухонная утварь", 2, "https://www.zwilling.com/it/utensili-da-cucina/strofinacci-da-cucina/"],

    # ["Хранение"],
    # ["Аксессуары хранение", "Хранение", 2, "https://www.zwilling.com/it/sistema-sottovuoto/accessori-per-sottovuoto/"],
    # ["Вакуумные насосы", "Хранение", 2, "https://www.zwilling.com/it/sistema-sottovuoto/pompa-per-sottovuoto/"],
    # ["Вакуумные пробки для вина", "Хранение", 2, "https://www.zwilling.com/it/sistema-sottovuoto/tappo-da-vino-sottovuoto/"],
    # ["Наборы для вакуумного хранения", "Хранение", 2, "https://www.zwilling.com/it/sistema-sottovuoto/primo-set-per-sottovuoto/"],
    # ["Пакеты для вакуумного хранения", "Хранение", 2, "https://www.zwilling.com/it/sistema-sottovuoto/sacchetti-sottovuoto/"],
    # ["Вакуумные контейнеры", "Хранение", 2, "https://www.zwilling.com/it/sistema-sottovuoto/contenitori-sottovuoto/"],
    # ["Ланч бокс в вакуумной упаковке", "Хранение", 2, "https://www.zwilling.com/it/sistema-sottovuoto/lunch-box-sottovuoto/"],

    # ["Сервировка стола"],
    # ["Посуда", "Сервировка стола", 2, "https://www.zwilling.com/it/servizi-per-la-tavola/servizi-tavola/"],
    # ["Столовые приборы", "Сервировка стола", 2, "https://www.zwilling.com/it/servizi-per-la-tavola/posate/"],
    # ["Стеклянная посуда", "Сервировка стола", 2, "https://www.zwilling.com/it/servizi-per-la-tavola/vetreria/"],
    # ["Стеклянная соломка", "Сервировка стола", 2, "https://www.zwilling.com/it/servizi-per-la-tavola/vetreria/cannucce-in-vetro/"],
    # ["Термо", "Сервировка стола", 2, "https://www.zwilling.com/it/servizi-per-la-tavola/thermo/"],
    # ["Соль и перец", "Сервировка стола", 2, "https://www.zwilling.com/it/servizi-per-la-tavola/sale-e-pepe/"],

    # ["Техника"],
    # ["Аксессуары техника", "Техника", 2, "https://www.zwilling.com/it/elettrodomestici-da-cucina/accessori/"],
    # ["Блендеры", "Техника", 2, "https://www.zwilling.com/it/elettrodomestici-da-cucina/frullatori/"],
    # ["Капучинаторы", "Техника", 2, "https://www.zwilling.com/it/elettrodomestici-da-cucina/macchine-caffe/"],
    # ["Тостеры", "Техника", 2, "https://www.zwilling.com/it/elettrodomestici-da-cucina/tostapane/"],
    # ["Чайники", "Техника", 2, "https://www.zwilling.com/it/elettrodomestici-da-cucina/bollitori-elettrici/"],
    # ["Кухонные весы", "Техника", 2, "https://www.zwilling.com/it/elettrodomestici-da-cucina/bilancia/"],
    # ["Машина для специй", "Техника", 2, "https://www.zwilling.com/it/elettrodomestici-da-cucina/macina-spezie/"],
    
    # ["Ножи"],
    # ["Блоки ножей", "Ножи", 2, "https://www.zwilling.com/it/coltelli/ceppi-di-coltelli/"],
    # ["Наборы ножей", "Ножи", 2, "https://www.zwilling.com/it/coltelli/set-di-coltelli/"],
    # ["Ножи для овощей", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-da-verdura/"],
    # ["Ножи для сыра", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-da-formaggio/"],
    # ["Филейные ножи", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-da-disosso/"],
    # ["Ножи сантоку", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-santoku/"],
    # ["Кухонные топорики", "Ножи", 2, "https://www.zwilling.com/it/coltelli/mannaia/"],
    # ["Стейковые ножи", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-da-bistecca/"],
    # ["Нож для мяса", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-da-carne/"],
    # ["Универсальные ножи", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-universali/"],
    # ["Ножи для хлеба", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-da-pane/"],
    # ["Аксессуары для заточки", "Ножи", 2, "https://zwilling.ru/catalog/nozhi/aksessuary_dlya_zatochki/"],
    # ["Поварские ножи", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-da-cuoco/"],
    # ["Нож для чистки овощей", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-spelucchino/"],
    # ["Нож для чистки картошки", "Ножи", 2, "https://www.zwilling.com/it/coltelli/pelapatate/"],
    # ["Китайский поварской нож", "Ножи", 2, "https://www.zwilling.com/it/coltelli/coltelli-da-cuoco-cinesi/"],
]
HEADERS = {
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Referer": "https://www.zwilling.com/it/outlet/",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
}

outlet_url = "https://www.zwilling.com/it/outlet/"
login = "manishin06@gmail.com"
password = "xYXA&]9n73z5J$j"

async def get_zwilling():
    image_links_dict = {}
    subcategories_dict = {}
    #запускаем парсинг ссылок аутлета в отдельном потоке. К моменту завершения парсинга осн. каталога, селениум уже давно завершит работу
    #outlet_parser = Outlet_parser()
    #outlet_parser.get_outlet()

    items = []
    # создаем категорию (проверка наличия уже в функции)
    category = crud.get_category(name=cat_name, metacategory=6)
    
    for subcategory in SUBCATEGORIES:
        if not str(subcategory[-1]).startswith('http'):
            if len(subcategory) == 1:
                crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            else:
                if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                    parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=category.id)
                    crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue

        base_link = subcategory[-1]
        logging.info(f'Starting {cat_name}: {subcategory[0]}')
        async with aiohttp.ClientSession(headers=HEADERS, trust_env=True) as session:
            async with session.get(base_link, ssl=False) as response:
                webpage = await response.text()
            urls = extract_urls(webpage)
            if not is_last_page(webpage):
                #pagination
                i = 1
                while True:
                    postfix = f"?PAGEN_1={i}&ajax_req=Y&selected=catalog_PRICE_3&order=ASC"
                    url = base_link + postfix
                    async with session.get(url, ssl=False) as response:
                        webpage = await response.text()
                        urls += extract_urls(webpage)
                        if is_last_page(webpage):
                            break
                        i += 1

            for url in urls[:5]:
                subcategories_dict[url] = subcategory[0]
                await asyncio.sleep(1)
                async with session.get(url, ssl=False) as response:
                    webpage = await response.text()
                    soup = bs(webpage, "html.parser")
                    try:
                        title = soup.find("span", attrs={"class" : "product-name"}).getText().strip()
                    except:
                        logging.warning("title")
                        
                    try:
                        #current_price = int((float(soup.find('span', attrs={"class" : "product-sales-price"}).text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                        current_price = int((float(soup.find('span', attrs={"class" : "product-sales-price"}).text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)) * float(f"1.{category.margin}"))
                    except:
                        logging.warning("price")
                        
                    try:
                        #old_price = int((float(soup.find('span', 'listprice-standard').text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                        old_price = int((float(soup.find('span', 'listprice-standard').text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)) * float(f"1.{category.margin}"))
                        #print([old_price])
                        percent = int(100 - float(current_price) / (float(old_price) / 100))
                    except:
                        old_price = None

                    description = ''
                    if old_price:
                        description = description[:700] + f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'

                    sizes = None

                    try:
                        image_links = []
                        # image_links = [img.get("src").replace("sw=100", "sw=350").replace("sh=100", "sh=350") for img in soup.find("div", attrs={"class" : "product-image-container"}).find_all("img")]
                        for img in soup.find("div", attrs={"class" : "product-image-container"}).find_all("img"):
                            try:
                                src = img.get("src")
                                if src:
                                    src = src.replace("sw=100", "sw=350").replace("sh=100", "sh=350")
                                    image_links.append(src)
                            except:
                                continue
                            
                    except Exception as err:
                        image_links = []
                        
                    image_links = image_links[:10]
                    image_links_dict[url] = image_links

                    article = url.split('.html')[0].split('/')[-1]

                    if not os.path.exists(f"database/images/{cat_name}"):
                        os.mkdir(f"database/images/{cat_name}")

                    if not os.path.exists(f"database/images/{cat_name}/{subcategory[0]}"):
                        os.mkdir(f"database/images/{cat_name}/{subcategory[0]}")
                    
                    i = urls.index(url) + 1
                    images = ''
                    
                    for link in image_links:
                        try:
                            num = image_links.index(link) + 1
                            img_path = f"database/images/{cat_name}/{subcategory[0]}/{i}_{title.replace(' ', '_').replace('/', '_')}_{num}.png"
                            if not os.path.exists(img_path):
                                async with session.get(link, ssl=False) as response:
                                    f = await aiofiles.open(img_path, mode='wb')
                                    await f.write(await response.read())
                                    await f.close()
                            images +=  img_path + '\n'
                        except:
                            continue

                    item = [title, description, current_price, images, sizes, article, url]
                    print(item)
                    items.append(item)
                    
    #получаем ссылки и цены, которые собрал селениум          
    outlet = outlet_parser.outlet
    #сохраняем аутлет отдельно, т к товары аутлета в обычном каталоге уже есть, то берем их, но цену из аутлета
    for i in range(len(items)):
        item = items[i]
        url = item[-1]
        if url in outlet.keys():
            print("есть аутлет")
            title = item[0]
            sizes = item[-3]
            image_links = image_links_dict[url]
            
            old_price = outlet[url]["old-price"]
            current_price = outlet[url]["current-price"]
            percent = int(100 - float(current_price) / (float(old_price) / 100))
            
            description = f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
            subcategory = subcategories_dict[url] + " аутлет"
            article = item[-2] + " outlet"
            
            if not os.path.exists(f"database/images/{cat_name}/{subcategory}"):
                os.mkdir(f"database/images/{cat_name}/{subcategory}")
            
            i = list(outlet.keys()).index(url) + 1
            images = ''
            
            for link in image_links:
                try:
                    num = image_links.index(link) + 1
                    img_path = f"database/images/{cat_name}/{subcategory}/{i}_{title.replace(' ', '_').replace('/', '_')}_{num}.png"
                    if not os.path.exists(img_path):
                        async with aiohttp.ClientSession(headers=HEADERS, trust_env=True) as session:
                            async with session.get(link, ssl=False) as response:
                                f = await aiofiles.open(img_path, mode='wb')
                                await f.write(await response.read())
                                await f.close()
                    images +=  img_path + '\n'
                except Exception as err:
                    print(err)
                    continue

            item = [title, description, current_price, images, sizes, article, url]
            print(item)
            items.append(item)
                  
def is_last_page(text : str) -> bool:
    soup = bs(text, "html.parser")
    load_more = soup.find("div", attrs={"class" : "laod-more-text"})
    return True if load_more is None else False
    
def extract_urls(text : str) -> list:
    base = "https://www.zwilling.com"

    soup = bs(text, "html.parser")
    products = soup.find_all("div", attrs={"class" : "inner-grid"})
    urls = []
    for product in products:
        try:
            url = base + product.find("div", attrs={"class" : "product-brand-name-wrapper"}).find("a").get("href")
            urls.append(url)
        except Exception as err:
            print(err)
            logging.warning("zwilling : problem with extracting url")
    return urls

class Outlet_parser():
    outlet = {}# {url : {"old-price" : '', "current-price" : ''}}
    
    def get_outlet(self):
        Thread(target=self.parsing).start()
        
    def parsing(self):
        driver = self.get_driver()

        driver.get(outlet_url)
        time.sleep(5)
        try:
            driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/a[1]").click()
            time.sleep(2)
            
            try:
                driver.find_element(By.XPATH, '//*[@id="dialog-container"]/div[2]/div[2]').click()
                time.sleep(2)
            except:
                pass
            
            driver.find_element(By.XPATH, '//*[@id="wrapper"]/div[3]/header/div[1]/div/div[4]/div[1]/div/span').click()
            time.sleep(3)
            
            driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/header/div[1]/div/div[4]/div[1]/div/div/div/span[1]").click()
            time.sleep(5)
            
            elem = driver.find_element(By.XPATH, '//*[@id="dwfrm_coRegisteredCustomer_email"]')
            elem.click()
            elem.send_keys(login)
            time.sleep(1)
            elem = driver.find_element(By.XPATH, '//*[@id="dwfrm_coRegisteredCustomer_password"]')
            elem.click()
            elem.send_keys(password)
            time.sleep(3)
            
            driver.find_element(By.XPATH, "/html/body/div[2]/div[10]/div[2]/div/div/div[2]/form/fieldset/div[3]/div/div[2]").click()
            time.sleep(10)
            
            self.show_more(driver)
            
            page = driver.page_source
            with open("site.html", "w", encoding="utf-8") as file:
                file.write(page)
            self.outlet = self.extract_outlet(page)
            print(self.outlet)
        except Exception as err:
            print(err)
        finally:
            driver.close()

    def show_more(self, driver):
        counter = 0
        while True:
            try:
                if counter > 10:
                    return
                counter += 1
                
                show_more = driver.find_elements(By.CSS_SELECTOR, ".show-more__link")
                if len(show_more) != 0:
                    self.scroll_to_show_more_and_click(driver, show_more[0])
                else:
                    return
            except Exception as err:
                print(err)
                return
            
    def scroll_to_show_more_and_click(self, driver, elem):
        counter = 0
        
        RESOLUTION = 1080
        while True:
            if counter > 50:
                break
            counter += 1
            
            driver.execute_script(f"window.scrollBy(0, {RESOLUTION/2})")
            try:
                elem.click()
                time.sleep(10)
                break
            except:
                continue
            
    def extract_outlet(self, webpage : str) -> dict:
        base = "https://www.zwilling.com"
        outlet = {}
        soup = bs(webpage, "html.parser")
        products = soup.find_all("div", attrs={"class" : "inner-grid"})
        for product in products:
            try:
                url =  base + product.find("div", attrs={"class" : "product-brand-name-wrapper"}).find("a").get("href")
                old_price  = int((float(product.find('span', attrs={"class" : "product-standard-price"}).text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                current_price = int((float(product.find('span', attrs={"class" : "product-sales-price"}).text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                outlet[url] = {"old-price" : old_price, "current-price" : current_price}
                
            except Exception as err:
                print(err)
                logging.warning("outlet problem")
        return outlet
    
    def get_driver(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--no-sandbox')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(executable_path="chromedriver.exe", options= options)
        
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source" : '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            '''
        })
        driver.maximize_window()
        return driver

if __name__ == "__main__":
    asyncio.run(get_zwilling())
    # p = Outlet_parser()
    # p.get_outlet()
