import asyncio
import aiohttp
import aiofiles
import logging
from bs4 import BeautifulSoup as bs
import os
import time

async def get_wolford():
    CAT_NAME = "Wolford"
    EURO_COSTS = euro_costs()
    SUBCATEGORIES = [
        # ["Новинки"],
        ["Трикотаж Новинки", "Новинки", 2, "https://www.wolfordshop.it/en/new-in/hosiery"],
        # ["Одежда", "Новинки", 2, "https://www.wolfordshop.it/en/new-in/clothing"],
        # ["Леггинсы Новинки", "Новинки", 2, "https://www.wolfordshop.it/en/new-in/leggings"],
        # ["Нижнее белье Новинки", "Новинки", 2, "https://www.wolfordshop.it/en/new-in/lingerie"],
        # ["Боди Новинки", "Новинки", 2, "https://www.wolfordshop.it/en/new-in/bodysuits"],
        # ["Пляжная одежда Новинки", "Новинки", 2, "https://www.wolfordshop.it/en/new-in/beachwear"],
        
        # ["Популярное Новинки", "Новинки"],
        # ["Гардероб MVP от WOLFORD", "Популярное Новинки", 3, "https://www.wolfordshop.it/en/mvp-x-wolford"],
        # ["Грейс Джонс х Вулфорд", "Популярное Новинки", 3, "https://www.wolfordshop.it/en/spring-summer-23-collection.html"],
        # ["Снова в наличии", "Популярное Новинки", 3, "https://www.wolfordshop.it/en/back-in-stock"],
        # ["The W Athleisure", "Популярное Новинки", 3, "https://www.wolfordshop.it/en/the-w-active"],
        
        # ["Трикотаж"],
        # ["Леггинсы Трикотаж", "Трикотаж", 2, "https://www.wolfordshop.it/en/hosiery/tights-leggings"],
        # ["Колготки", "Трикотаж", 2, "https://www.wolfordshop.it/en/hosiery/tights"],
        # ["Оставайтесь на связи", "Трикотаж", 2, "https://www.wolfordshop.it/en/hosiery/stay-ups"],
        # ["Гольфы и гольфы выше колен", "Трикотаж", 2, "https://www.wolfordshop.it/en/hosiery/knee-highs-and-overknees"],
        # ["Носки", "Трикотаж", 2, "https://www.wolfordshop.it/en/hosiery/socks"],
        
        # ["Популярное Трикотаж", "Трикотаж", 2],
        # ["Набор ограниченной серии", "Популярное Трикотаж", 3, "https://www.wolfordshop.it/en/hosiery/limited-special-edition"],
        # ["Легендарные леггинсы", "Популярное Трикотаж", 3, "https://www.wolfordshop.it/en/iconic-legwear.html"],
        # ["Прозрачные колготки", "Популярное Трикотаж", 3, "https://www.wolfordshop.it/en/hosiery/sheer-tights"],
        # ["Непрозрачные колготки", "Популярное Трикотаж", 3, "https://www.wolfordshop.it/en/hosiery/opaque-tights"],
        # ["Моделирующие колготки", "Популярное Трикотаж", 3, "https://www.wolfordshop.it/en/hosiery/support-tights"],
        # ["Модные колготки", "Популярное Трикотаж", 3, "https://www.wolfordshop.it/en/hosiery/favourite-tights"],
        
        # ["Одежда и боди"],
        # ["Боди", "Одежда и боди", 2, "https://www.wolfordshop.it/en/clothing-and-bodywear/bodysuits"], 
        # ["Леггинсы Одежда и боди", "Одежда и боди", 2, "https://www.wolfordshop.it/en/clothing-and-bodywear/leggings"], 
        # ["Платья", "Одежда и боди", 2, "https://www.wolfordshop.it/en/clothing-and-bodywear/dresses"], 
        # ["Топы и футболки", "Одежда и боди", 2, "https://www.wolfordshop.it/en/clothing-and-bodywear/tops-and-t-shirts"], 
        # ["Пуловеры и водолазки", "Одежда и боди", 2, "https://www.wolfordshop.it/en/clothing-and-bodywear/pullovers-and-turtlenecks"], 
        # ["Юбки", "Одежда и боди", 2, "https://www.wolfordshop.it/en/clothing-and-bodywear/skirts"], 
        # ["Брюки и комбинезоны", "Одежда и боди", 2, "https://www.wolfordshop.it/en/clothing-and-bodywear/trousers-and-jumpsuits"], 
        # ["Кардиганы и куртки", "Одежда и боди", 2, "https://www.wolfordshop.it/en/clothing-and-bodywear/cardigans-and-jackets"], 
        # ["Аксессуары", "Одежда и боди", 2, "https://www.wolfordshop.it/en/clothing-and-bodywear/accessories"], 
        
        # ["Популярное Одежда и боди", "Одежда и боди"],
        # ["Спорт", "Популярное Одежда и боди", 3, "https://www.wolfordshop.it/en/the-w-active"],
        # ["Меринос и кашемир", "Популярное Одежда и боди", 3, "https://www.wolfordshop.it/en/merino-and-cashmere"],
        # ["Роковое платье", "Популярное Одежда и боди", 3, "https://www.wolfordshop.it/en/fatal-dress.html"],
        # ["Корректирующие платья", "Популярное Одежда и боди", 3, "https://www.wolfordshop.it/en/clothing-and-bodywear/shaping-dresses"],
        
        # ["Леггинсы", "https://www.wolfordshop.it/en/leggings/tights-leggings"],
        # ["Модные леггинсы", "Леггинсы", 2, "https://www.wolfordshop.it/en/leggings/fashion-leggings"],
        # ["Спортивные леггинсы", "Леггинсы", 2, "https://www.wolfordshop.it/en/leggings/athleisure-leggings"],
        
        # ["Нижнее белье"],
        # ["Пляжная одежда", "Нижнее белье", 2, "https://www.wolfordshop.it/en/lingerie/beachwear"],
        # ["Бюстгальтеры", "Нижнее белье", 2, "https://www.wolfordshop.it/en/lingerie/bras"],
        # ["Трусы", "Нижнее белье", 2, "https://www.wolfordshop.it/en/lingerie/briefs"],
        # ["Нижнее белье Боди", "Нижнее белье", 2, "https://www.wolfordshop.it/en/lingerie/lingerie-bodysuits"],
        # ["Топы и платья", "Нижнее белье", 2, "https://www.wolfordshop.it/en/lingerie/tops-and-dresses"],
        
        # ["Популярное Нижнее белье", "Нижнее белье"],
        # ["Коллекция 3W", "Популярное Нижнее белье", 3, "https://www.wolfordshop.it/en/3w-lingerie-collection.html"],
        # ["Корректирующее белье", "Популярное Нижнее белье", 3, "https://www.wolfordshop.it/en/lingerie/shaping-lingerie"],
        # ["Men", "Популярное Нижнее белье", 3, "https://www.wolfordshop.it/en/lingerie/men"],
        
        # ["Основные моменты"],
        # ["Иконки", "Основные моменты", 3, "https://www.wolfordshop.it/en/highlights/icons"],
        # ["Меринос и кашемир", "Основные моменты", 3, "https://www.wolfordshop.it/en/merino-and-cashmere"],
        # ["Корректирующее белье", "Основные моменты", 3, "https://www.wolfordshop.it/en/highlights/shapewear"],
        # ["Материнство", "Основные моменты", 3, "https://www.wolfordshop.it/en/highlights/maternity"],
        # ["Men", "Основные моменты", 3, "https://www.wolfordshop.it/en/highlights/men"],
        # ["Маски для ухода", "Основные моменты", 3, "https://www.wolfordshop.it/en/highlights/care-masks"],
        # ["Веганская кожа", "Основные моменты", 3, "https://www.wolfordshop.it/en/highlights/vegan-leather"],
        
        # ["Популярное Основные моменты", "Основные моменты", 2],
        # ["N21XWolford", "Популярное Основные моменты", 3, "https://www.wolfordshop.it/en/n21-x-wolford"],
        # ["Бестселлеры", "Популярное Основные моменты", 3, "https://www.wolfordshop.it/en/most-wanted"],
        # ["Снова в наличии Основные моменты", "Популярное Основные моменты", 3, "https://www.wolfordshop.it/en/most-wanted"],
        # ["Аврора - Экологическая коллекция", "Популярное Основные моменты", 3, "https://www.wolfordshop.it/en/highlights/sustainable-collection"],
            
        # ["The W Active"],
        # ["Леггинсы The W Active", "The W Active", 2, "https://www.wolfordshop.it/en/the-w-active/leggings"],
        # ["Топы и футболки The W Active", "The W Active", 2, "https://www.wolfordshop.it/en/the-w-active/tops-and-t-shirts"],
        # ["Носки и гольфы The W Active", "The W Active", 2, "https://www.wolfordshop.it/en/the-w-active/socks-and-knee-highs"],
        # ["Кардиганы и куртки The W Active", "The W Active", 2, "https://www.wolfordshop.it/en/the-w-active/cardigans-and-jackets"],
        # ["Брюки и комбинезоны The W Active", "The W Active", 2, "https://www.wolfordshop.it/en/the-w-active/trousers-and-jumpsuits"],
        # ["Боди The W Active", "The W Active", 2, "https://www.wolfordshop.it/en/the-w-active/bodysuits"],
        # ["Платья The W Active", "The W Active", 2, "https://www.wolfordshop.it/en/the-w-active/dresses"],
        
        # ["Популярное The W Active", "The W Active"],
        # ["Чудо леггинсы Wolford", "Популярное The W Active", 3, "https://www.wolfordshop.it/en/the-w-active/dresses"],
        # ["Трейси Андерсон для Wolford", "Популярное The W Active", 3, "https://www.wolfordshop.it/en/tracy-anderson-edit.html"],
        # ["Kalon Movement x Wolford", "Популярное The W Active", 3, "https://www.wolfordshop.it/en/tracy-anderson-edit.html"],
        
        # ["Аутлет"],
        # ["Новинки Аутлет", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/new-in"],
        # ["Трикотаж Аутлет", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/hosiery"],
        # ["Леггинсы Аутлет", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/leggings"],
        # ["Боди Аутлет", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/bodysuits"],
        # ["Одежда Аутлет", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/clothing"],
        # ["Нижнее белье Аутлет", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/lingerie"],
        # ["Пляжная одежда Аутлет", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/beachwear"],
        # ["Аксессуары Аутлет", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/accessories"],
        # ["Red Label Extra 30", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/red-label"],
        # ["35% OFF", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/-35-"],
        # ["50% OFF", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/-35-"],
        # ["The W", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/the-w"],
        # ["Коллаборации", "Аутлет", 2, "https://www.wolfordshop.it/en/outlet/collabs"],
    ]
    HEADERS = {
        "Host": "www.wolfordshop.it",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User":"?1",
    }
    for subcategory in SUBCATEGORIES:
        items = []
        subcategory_link = subcategory[-1]
        async with aiohttp.ClientSession(headers=HEADERS, trust_env=True) as session:
            def extract_links_from_page(webpage : str) -> list:
                soup = bs(webpage, "html.parser")
                try:
                    product_panel = soup.find("ul", attrs={"class" : "js-product-tiles"})
                    product_urls = [i.find("a").get("href") for i in product_panel.find_all("li", attrs={"class" : "js-product-tile"})]
                    return product_urls
                except:
                    return []
                
            product_urls = []
            counter = 1
            while True:
                url = subcategory_link + f"?page={counter}"
                async with session.get(url, ssl = False) as response:
                    webpage = await response.text()
                addictional_urls = extract_links_from_page(webpage)
                if len(addictional_urls) == 0:
                    break
                product_urls += addictional_urls
                counter += 1
            
            for product_url in product_urls:
                try:
                    async with session.get(product_url, ssl = False) as response:
                        webpage = await response.text()
                    soup = bs(webpage, "html.parser")
                    
                    try:
                        title = soup.find("h1", attrs={"itemprop" : "name"}).getText().strip(" \n\r")
                    except:
                        pass
                    
                    try:
                        prices = soup.find("div", attrs={"class" : "js-product-pricing"})
                        old_price_tag = prices.find("span", attrs={"class" : "price-old"})
                        if old_price_tag:
                            old_price = int((float(old_price_tag.getText().strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                        else:
                            old_price = None
                        current_price = int((float(prices.find("span", attrs={"class" : "price-new"}).getText().strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                    except:
                        pass
                    
                    try:
                        description = soup.find("div", attrs={"class" : "accordion-content"}).getText().strip(" \n\r")[:700]
                    except Exception as err:
                        print(err)
                    
                    if old_price:
                        percent = int(100 - float(current_price) / (float(old_price) / 100))
                        description = description[:700] + f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                    
                    try:
                        sizes = [opt.getText().split("-")[0].strip().replace("\n", "") for opt in soup.find("select", attrs={"id" : "va-size"}).find_all("option")]
                        for size in sizes:
                            if "Choose" in size:
                                sizes.remove(size)
                        
                        if len(sizes) != 0:
                            sizes = ", ".join(sizes)
                            description += '\n\nРазмеры:\n' + sizes
                        else:
                            sizes = ""
                    except:
                        sizes = ""
                        
                    article = product_url.split("/")[-1].split(".html")[0]
                    try:
                        base = "https://www.wolfordshop.it/dw/image/v2/BBCH_PRD"
                        image_links = [image.get("data-src") for image in soup.find("div", attrs={"class" : "pdp-main-media"}).find_all("img")]
                        for i in range(len(image_links)):
                            image_link = image_links[i]
                            if "https:" not in image_link:
                                image_links[i] = base + image_link
                    except:
                        image_links = []
                        
                    i = product_urls.index(product_url) + 1
                    images = ''
                    
                    if not os.path.exists(f"database/images/{CAT_NAME}"):
                            os.mkdir(f"database/images/{CAT_NAME}")

                    if not os.path.exists(f"database/images/{CAT_NAME}/{subcategory[0]}"):
                        os.mkdir(f"database/images/{CAT_NAME}/{subcategory[0]}")

                    for link in image_links:
                        try:
                            num = image_links.index(link) + 1
                            img_path = f"database/images/{CAT_NAME}/{subcategory[0]}/{i}_{title.replace(' ', '_').replace('/', '_')}_{num}.jpg"
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
                    
                        
                except Exception as err:
                    logging.warning(f'{CAT_NAME} pr - {err}')
                    
            
if __name__ == "__main__":
    asyncio.run(get_wolford())
            