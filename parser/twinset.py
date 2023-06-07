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
#https://www.twinset.com/en-it/outlet/
CAT_NAME = "Twinset"
EURO_COSTS = 87

SUBCATEGORIES = [
    # ["Новинки", 1, "https://www.twinset.com/en-it/new-arrivals/"],
    
    # #clothing
    # ["Одежда", 1, "https://www.twinset.com/en-it/clothing/"],
    ['Одежда'],
    ["Платья", "Одежда", 2, "https://www.twinset.com/en-it/clothing/dresses/"],
    
    ["Короткие платья", "Платья", 3, "https://www.twinset.com/en-it/clothing/dresses/short-dresses/" ],
    ["Длинные платья", "Платья", 3, "https://www.twinset.com/en-it/clothing/dresses/long-dresses/" ],
    # ["Платья с длинными рукавами", "Платья", "Одежда", 3, "https://www.twinset.com/en-it/clothing/dresses/longuette-dresses/" ],
    # ["Вязаные платья", "Платья", "Одежда", 3, "https://www.twinset.com/en-it/clothing/dresses/knitted-dresses/" ],
    # ["Платья-рубашки", "Платья", "Одежда", 3, "https://www.twinset.com/en-it/clothing/dresses/shirt-dresses/" ],
    # ["Кружевные платья", "Платья", "Одежда", 3, "https://www.twinset.com/en-it/clothing/dresses/lace-dresses/" ],
    # ["Элегантные платья", "Платья", "Одежда", 3, "https://www.twinset.com/en-it/clothing/dresses/elegant-dresses/" ],
    # ["Вечерние платья", "Платья", "Одежда", 3, "https://www.twinset.com/en-it/clothing/dresses/formal-dresses/" ],
    # ["Rомбинезоны", "Платья", "Одежда", 3, "https://www.twinset.com/en-it/clothing/dresses/jumpsuits/" ],
    
    # ["Джемперы и кардиганы", "Одежда", 2, "https://www.twinset.com/en-it/clothing/jumpers-and-cardigans/"],
    # ["Блузки и рубашки", "Одежда", 2, "https://www.twinset.com/en-it/clothing/blouses-and-shirts/"],
    # ["Футболки и топы", "Одежда", 2, "https://www.twinset.com/en-it/clothing/t-shirts-and-tops/"],
    # ["Толстовки", "Одежда", 2, "https://www.twinset.com/en-it/clothing/sweatshirts/"],
    # ["Джинсы", "Одежда", 2, "https://www.twinset.com/en-it/clothing/jeans/"],
    # ["Юбки", "Одежда", 2, "https://www.twinset.com/en-it/clothing/skirts/"],
    # ["Брюки", "Одежда", 2, "https://www.twinset.com/en-it/clothing/trousers/"],
    # ["Костюмы и комплекты", "Одежда", 2, "https://www.twinset.com/en-it/clothing/suits-and-sets/"],
    # ["Нижнее белье и одежда для сна", "Одежда", 2, "https://www.twinset.com/en-it/clothing/underwear-and-nightwear/"],
    
    # ["Куртки и верхняя одежда", "Одежда", 2, ""],
    # ["Блейзеры", "Куртки и верхняя одежда", "Одежда", 3, "https://www.twinset.com/en-it/clothing/jackets-and-outerwear/blazers/"],
    # ["Куртки и пуховики", "Куртки и верхняя одежда", "Одежда", 3, "https://www.twinset.com/en-it/clothing/jackets-and-outerwear/jackets-and-puffer-jackets/"],
    # ["Пальто и тренчи", "Куртки и верхняя одежда", "Одежда", 3, "https://www.twinset.com/en-it/clothing/jackets-and-outerwear/coats-and-trench-coats/"],
    # ["Пончо", "Куртки и верхняя одежда", "Одежда", 3, "https://www.twinset.com/en-it/clothing/jackets-and-outerwear/ponchos/"],
    
    # ["Пляжная одежда", "Одежда", 2, "https://www.twinset.com/en-it/clothing/beachwear/"],
    # ["Бикини", "Пляжная одежда", "Одежда", 3, "https://www.twinset.com/en-it/clothing/beachwear/bikini/"],
    # ["Купальники", "Пляжная одежда", "Одежда", 3, "https://www.twinset.com/en-it/clothing/beachwear/swimsuits/"],
    # ["Пляжная одежда и аксессуары", "Пляжная одежда", "Одежда", 3, "https://www.twinset.com/en-it/clothing/beachwear/beachwear-and-accessories/"],

    # ["Покупки по вдожновению", "Одежда", 2, "https://www.twinset.com/en-it/clothing/shop-by-inspiration/"],
    # ["Летние флюиды", "Покупки по вдожновению", "Одежда", 3, "https://www.twinset.com/en-it/clothing/shop-by-inspiration/summer-vibes/"],
    # ["Очаровательный Нуар", "Покупки по вдожновению", "Одежда", 3, "https://www.twinset.com/en-it/clothing/shop-by-inspiration/charming-noir/"],
    # ["Наилучшее", "Покупки по вдожновению", "Одежда", 3, "https://www.twinset.com/en-it/clothing/shop-by-inspiration/most-loved/"],

    # ["Одежда по случаю", "Одежда", 2, "https://www.twinset.com/en-it/clothing/shop-by-occasion/"],
    # ["Официальные мероприятия", "Одежда по случаю", "Одежда", 3, "https://www.twinset.com/en-it/clothing/shop-by-occasion/formal-events/"],
    # ["Вечеринка", "Одежда по случаю", "Одежда", 3, "https://www.twinset.com/en-it/clothing/shop-by-occasion/party/"],
    # ["Свадьба", "Одежда по случаю", "Одежда", 3, "https://www.twinset.com/en-it/clothing/shop-by-occasion/wedding/"],
    # ["Выпускной", "Одежда по случаю", "Одежда", 3, "https://www.twinset.com/en-it/clothing/shop-by-occasion/graduation/"],
    # ["Бизнес", "Одежда по случаю", "Одежда", 3, "https://www.twinset.com/en-it/clothing/shop-by-occasion/business/"],
    # ["Для путешествий", "Одежда по случаю", "Одежда", 3, "https://www.twinset.com/en-it/clothing/shop-by-occasion/travel/"],
    
    
    # #bags
    ['Сумки'],
    #["Сумки", 1, "https://www.twinset.com/en-it/bags/"],
    ["Сумки через плечо", "Сумки", 2, "https://www.twinset.com/en-it/bags/cross-body-bags/"],
    ["Сумки на плечо", "Сумки", 2, "https://www.twinset.com/en-it/bags/shoulder-bags/"],
    # ["Дамские сумочки", "Сумки", 2, "https://www.twinset.com/en-it/bags/handbags/"],
    # ["Сумки для покупок", "Сумки", 2, "https://www.twinset.com/en-it/bags/shopping-bags/"],
    # ["Сумки Хобо", "Сумки", 2, "https://www.twinset.com/en-it/bags/hobo-bags/"],
    # ["Клатчи", "Сумки", 2, "https://www.twinset.com/en-it/bags/clutch-bags/"],
    # ["Мини-сумки", "Сумки", 2, "https://www.twinset.com/en-it/bags/mini-bags/"],
    

    # #shoes
    ['Обувь'],
    # ["Обувь", 1, "https://www.twinset.com/en-it/shoes/"],
    ["Кроссовки", "Обувь", 2, "https://www.twinset.com/en-it/shoes/sneakers/"],
    # ["Туфли-лодочки и сандалии", "Обувь", 2, "https://www.twinset.com/en-it/shoes/court-shoes-and-sandals/"],
    # ["Сапоги и ботильоны", "Обувь", 2, "https://www.twinset.com/en-it/shoes/boots-and-ankle-boots/"],
    # ["Боевые сапоги", "Обувь", 2, "https://www.twinset.com/en-it/shoes/combat-boots/"],
    # ["Обувь на плоской подошве", "Обувь", 2, "https://www.twinset.com/en-it/shoes/flat-shoes/"],
    # ["Каблуки", "Обувь", 2, "https://www.twinset.com/en-it/shoes/heels/"],
    
    
    # #accessories
    
    ["Аксессуары"],
    ["Ювелирные изделия", "Аксессуары", 2, "https://www.twinset.com/en-it/accessories/jewellery/"],
    # ["Ремни", "Аксессуары", 2, "https://www.twinset.com/en-it/accessories/belts/"],
    # ["Шарфы", "Аксессуары", 2, "https://www.twinset.com/en-it/accessories/scarves/"],
    # ["Головные уборы", "Аксессуары", 2, "https://www.twinset.com/en-it/accessories/hats/"],
    # ["Кошельки и брелоки", "Аксессуары", 2, "https://www.twinset.com/en-it/accessories/wallets-and-keyrings/"],
    # ["Солнечные очки", "Аксессуары", 2, "https://www.twinset.com/en-it/accessories/sunglasses/"],
    # ["Другие аксессуары", "Аксессуары", 2, "https://www.twinset.com/en-it/accessories/other-accessories/"],

    # #actitude
    # ["Коллекция Actitude", 1, "https://www.twinset.com/en-it/actitude/"],
    # ["Платья Actitude","Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/dresses/"],
    # ["Джемперы и кардиганы Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/jumpers-and-cardigans/"],
    # ["Блузки и рубашки Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/blouses-and-shirts/"],
    # ["Толстовки Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/sweatshirts/"],
    # ["Футболки и топы Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/t-shirts-and-tops/"],
    # ["Юбки Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/skirts/"],
    # ["Джинсы Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/jeans/"],
    # ["Брюки Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/trousers/"],
    # ["Куртки и верхняя одежда Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/jackets-and-outerwear/"],
    # ["Аксессуары Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/accessories/"],
    # ["Сумки Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/bags/"],
    # ["Обувь Actitude", "Коллекция Actitude", 2, "https://www.twinset.com/en-it/actitude/shoes/"],
    
    # #girls
    ["Для девочек"],
    ["Платья для девочек", "Для девочек", 2, "https://www.twinset.com/en-it/girl/dresses/"],
    ["Футболки и топы для девочек", "Для девочек", 2, "https://www.twinset.com/en-it/girl/t-shirts-and-tops/"],
    # ["Блузки и рубашки для девочек", "Для девочек", 2, "https://www.twinset.com/en-it/girl/blouses-and-shirts/"],
    # ["Джемперы и кардиганы для девочек", "Для девочек", 2, "https://www.twinset.com/en-it/girl/jumpers-and-cardigans/"],
    # ["Юбки для девочек", "Для девочек", 2, "https://www.twinset.com/en-it/girl/skirts/"],
    # ["Брюки и джинсы для девочек", "Для девочек", 2, "https://www.twinset.com/en-it/girl/trousers-and-jeans/"],
    # ["Наборы для девочек", "Для девочек", 2, "https://www.twinset.com/en-it/girl/sets/"],
    # ["Куртки и верхняя одежда для девочек", "Для девочек", 2, "https://www.twinset.com/en-it/girl/jackets-and-outerwear/"],
    # ["Аксессуары для девочек", "Для девочек", 2, "https://www.twinset.com/en-it/girl/accessories/"],
    # ["Обувь для девочек", "Для девочек", 2, "https://www.twinset.com/en-it/girl/shoes/"],
    # ["Малышка", "Для девочек", 2, "https://www.twinset.com/en-it/girl/baby-girl/"],

    # #outlet
    ["Аутлет"],
    ["Аксессуары аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Accessories"],
    ["Сумки аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Bags"],
    # ["Пляжная одежда аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Beachwear"],
    # ["Блузки аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Blouses"],
    # ["Кардиганы аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Cardigans"],
    # ["Платья аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Dresses"],
    # ["Коллекция для девочек аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Girls' collection"],
    # ["Джинсы аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Jeans"],
    # ["Джемперы аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Jumpers"],
    # ["Верхняя одежда аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Outerwear"],
    # ["Рубашки аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Shirts"],
    # ["Обувь аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Shoes"],
    # ["Юбки аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Skirts"],
    # ["Толстовки аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Sweatshirts"],
    # ["Топы аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Tops"],
    # ["Брюки аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Trousers"],
    # ["Футболки аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=T-shirts"],
    # ["Нижнее белье и одежда для сна аутлет", "Аутлет", 2, "https://www.twinset.com/en-it/outlet/?prefn1=microCategorySearch&prefv1=Underwear and Nightwear"],
]

HEADERS = {
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
}

async def get_twinset():
    
    
    for subcategory in SUBCATEGORIES:
        if not str(subcategory[-1]).startswith('http'):
            if len(subcategory) == 1:
                crud.create_subcategory(name=subcategory[0], category=cat_name) if not crud.subcategory_exists(name=subcategory[0], category=cat_name) else 0
            else:
                if not crud.subcategory_exists(name=subcategory[0], category=cat_name):
                    parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=category.id)
                    crud.create_subcategory(name=subcategory[0], category=cat_name, parent_subcategory=parent_subcategory.id, level=subcategory[2])
            continue
        items = []
        subcategory_link = subcategory[-1]
        async with aiohttp.ClientSession(headers=HEADERS, trust_env=True) as session:
            async with session.get(subcategory_link, ssl=False) as response:
                webpage = await response.text()
            soup = bs(webpage, "html.parser")   
            product_urls = extract_links(soup)

            while is_next_page_existing(soup):
                next_page_link = get_link_to_next_page(soup)
                async with session.get(next_page_link, ssl=False) as response:
                    webpage = await response.text()
                soup = bs(webpage, "html.parser")
                product_urls += extract_links(soup)
                
            for product_url in product_urls[:5]:
                try:
                    await asyncio.sleep(1)
                    async with session.get(product_url, ssl=False) as response:
                        webpage = await response.text()
                    soup = bs(webpage, "html.parser")
                    
                    try:
                        title = soup.find("h1", attrs={"class" : "product-name"}).getText()
                    except:
                        pass
                    
                    try:
                        image_links = [i.get("src") for i in soup.find("div", attrs={"class" : "side-grid-images"}).find_all("img")][:10]
                    except Exception as err:
                        print(err)
                        image_links = []
                        
                    price_wrapper = soup.find("span", attrs={"class" : "price-wrapper"})
                    try:
                        current_price = int((float(price_wrapper.find("span", attrs={"class" : "sales value"}).getText().strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                    except:
                        pass
                    
                    try:
                        old_price = int((float(price_wrapper.find('span', attrs={"class" : "strike-through"}).getText().strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                        #print([old_price])
                        percent = int(100 - float(current_price) / (float(old_price) / 100))
                    except:
                        old_price = None
                        
                    description = get_description_from_soup(soup)
                    if old_price:
                        description = description[:700] + f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                    
                    try:
                        sizes = [i.getText().strip(" \n") for i in soup.find("ul", attrs={"class" : "list-size"}).find_all("li")]
                        sizes = ", ".join(sizes)
                        description += '\n\nРазмеры:\n' + sizes
                    except Exception as err:
                        print(err)
                        pass
                    
                    article = product_url.split('.html')[0].split('/')[-1].split("-")[-1]
                    
                    i = product_urls.index(product_url) + 1
                    images = ''
                    
                    if not os.path.exists(f"database/images/{CAT_NAME}"):
                            os.mkdir(f"database/images/{CAT_NAME}")

                    if not os.path.exists(f"database/images/{CAT_NAME}/{subcategory[0]}"):
                        os.mkdir(f"database/images/{CAT_NAME}/{subcategory[0]}")

                    for link in image_links:
                        try:
                            num = image_links.index(link) + 1
                            img_path = f"database/images/{CAT_NAME}/{subcategory[0]}/{i}_{title.replace(' ', '_').replace('/', '_')}_{num}.png"
                            if not os.path.exists(img_path):
                                async with session.get(link, ssl=False) as response:
                                    f = await aiofiles.open(img_path, mode='wb')
                                    await f.write(await response.read())
                                    await f.close()
                            images +=  img_path + '\n'
                        except Exception as err:
                            print(err)

                    item = [title, description, current_price, images, sizes, article, product_url]
                    print(item)
                    items.append(item)
                    
                except Exception as ex:
                    logging.warning(f'{CAT_NAME} pr - {ex}')
        
        ## добавляем товары
        if not crud.subcategory_exists(name=subcategory[0], category=CAT_NAME):
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=crud.get_category(name=CAT_NAME).id)
            crud.create_subcategory(name=subcategory[0], category=CAT_NAME, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        await crud.create_products(category=CAT_NAME, subcategory=subcategory[0], items=items)
            
            
                           
def extract_links(soup : bs) -> list:
    base = "https://www.twinset.com"
    try:
        product_panel = soup.find("div", attrs={"id" : "product-search-results"})
        if product_panel is not None:
            product_urls = [base + i.get("href") for i in product_panel.find_all("a", attrs={"class" : "image-link"})]
        else:
            product_urls = [base + i.get("href") for i in soup.find_all("a", attrs={"class" : "image-link"})]
    except:
        return []
    
    print(f"len = {len(product_urls)}")
    return product_urls

def is_next_page_existing(soup : bs) -> bool:
    elems = soup.find_all("li", attrs={"class" : "pagination-next"})
    if len(elems) == 0:
        return False
    else: 
        return True
            
def get_link_to_next_page(soup : bs) -> str:
    link = soup.find("li", attrs={"class" : "pagination-next"}).find("button").get("data-url")
    return link

def get_description_from_soup(soup : bs) -> str:
    try:
        panel = soup.find("div", attrs={"class" : "primary-image-description"})
        paragraphs = [i.getText().strip(" \n") for i in panel.find_all("div")]
        description = "\n".join(paragraphs)
    except:
        description = ""
    return description

if __name__ == "__main__":
    asyncio.run(get_twinset())
            
             