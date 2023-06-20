import asyncio
import aiohttp
import aiofiles
import logging
from bs4 import BeautifulSoup as bs
import re
import os
import json

async def get_odlo():
    headers = {
        'dwac_5472789576bff66ffd4618ca57': 'ET9hQAHAOvBasZ3rBtrZiBhPI707sy-6T9I^%^3D^|dw-only^|^|^|USD^|false^|US^%^2FEastern^|true',
        'cqcid': 'abtFRBhhgb8xGttobIUMX2heFx',
        'cquid': '^|^|',
        'selectedSite': 'odlo-eu',
        'sid': 'ET9hQAHAOvBasZ3rBtrZiBhPI707sy-6T9I',
        'selectedCountry': 'IT',
        'selectedLocale': 'en_IT',
        'dwanonymous_fdc878cb7d0265df285cfb344b0a908d': 'bcTUYNmKQ0ADXIIfaPoyR0DD1j',
        '__cq_dnt': '0',
        'dw_dnt': '0',
        'dwsid': 'PH17dWJkzznuvCUE41y9CzUNOYhYF9pz-9-Zg3OnUrweYCpU32ghBrFS5kpp16J90Ux3V20kSN5HdElUUYDSOg==',
        'dwac_e993e0dda9f8aba4be0dd1d5b5': 'ET9hQAHAOvBasZ3rBtrZiBhPI707sy-6T9I^%^3D^|dw-only^|^|^|EUR^|false^|Europe^%^2FZurich^|true',
        'dwanonymous_0d26e963a726eb06a7405bc2d1ce4c6b': 'abtFRBhhgb8xGttobIUMX2heFx',
        'hideNewsletterPopup': 'true',
    }
    data = {
        'dwfrm_countrychange_country': 'IT',
        'dwfrm_countrychange_language': 'en_IT',
        'dwfrm_countrychange_urlparams': 'eyJhY3Rpb24iOiJTZWFyY2gtU2hvdyIsInBhcmFtcyI6WyJjZ2lkIiwid29tZW4taGVhZHdlYXItZ2xvdmVzIl19',
        'dwfrm_countrychange_apply': 'Apply',
    }
    EURO_COSTS = 67
    CAT_NAME = "odlo"
    SUBCATEGORIES = [
        ["Женщины"],
        
        ["Женщины распродажа", "Женщины", 2, "https://www.odlo.com/it/en/women/sale/"],
        
        ["Женская одежда", "Женщины"],
        ["Женщины нижний слой (куртки)", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/base-layers/"],
        ["Женщины нижнее белье", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/underwear/"],
        ["Женщины Спортивные бюстгальтеры", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/sports-bras/"],
        ["Женщины футболки и поло", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/t-shirts-polos/"],
        ["Женщины шорты", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/shorts/"],
        ["Женщины брюки и колготки", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/pants-tights/"],
        ["Женщины средние слои (куртки) и длинные рукава", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/mid-layers-longsleeves/"],
        ["Женщины куртки и жилеты", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/jackets-vests/"],
        ["Женщины носки", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/socks/"],
        ["Женщины головной убор и перчатки", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/headwear-gloves/"],
        ["Женщины другие аксессуары", "Женская одежда", 3, "https://www.odlo.com/it/en/women/apparel/other-accessories/"],
        
        ["Женщины спорт", "Женщины"],
        ["Женщины бег", "Женщины спорт", 3, "https://www.odlo.com/it/en/women/sports/running/"],
        ["Женщины тренировки", "Женщины спорт", 3, "https://www.odlo.com/it/en/women/sports/training/"],
        ["Женщины езда на велосипеде", "Женщины спорт", 3, "https://www.odlo.com/it/en/women/sports/cycling/"],
        ["Женщины пеший туризм", "Женщины спорт", 3, "https://www.odlo.com/it/en/women/sports/hiking/"],
        ["Женщины Everyday 365", "Женщины спорт", 3, "https://www.odlo.com/it/en/women/sports/everyday-365/"],
        ["Женщины лыжи и снег", "Женщины спорт", 3, "https://www.odlo.com/it/en/women/sports/ski-snow/"],
        ["Женщины скиатлон", "Женщины спорт", 3, "https://www.odlo.com/it/en/women/sports/cross-country-skiing/"],
        
        ["Женщины технологии", "Женщины"],
        ["Женщины Active Spine", "Женщины технологии", 3, "https://www.odlo.com/it/en/women/technologies/active-spine/"],
        ["Женщины Dual Dry", "Женщины технологии", 3, "https://www.odlo.com/it/en/women/technologies/dual-dry/"],
        ["Женщины Chill-Tec", "Женщины технологии", 3, "https://www.odlo.com/it/en/women/technologies/chill-tec/"],
        ["Женщины F-Dry", "Женщины технологии", 3, "https://www.odlo.com/it/en/women/technologies/f-dry/"],
        ["Женщины Ceramicool", "Женщины технологии", 3, "https://www.odlo.com/it/en/women/technologies/ceramicool/"],
        ["Женщины Linencool", "Женщины технологии", 3, "https://www.odlo.com/it/en/women/technologies/linencool/"],
        ["Женщины Performance wool", "Женщины технологии", 3, "https://www.odlo.com/it/en/women/technologies/performance-wool/"],
        ["Женщины ZeroScent", "Женщины технологии", 3, "https://www.odlo.com/it/en/women/technologies/zeroscent/"],

        ["Женщины рекомендуемое", "Женщины"],
        ["Женщины бестселлеры", "Женщины рекомендуемое", 3, "https://www.odlo.com/it/en/women/featured/bestsellers/"],
        ["Женщины гид по нижнему слою (куртки)", "Женщины рекомендуемое", 3, "https://www.odlo.com/it/en/women/featured/base-layer-guide/"],
        ["Женщины экологичная одежда", "Женщины рекомендуемое", 3, "https://www.odlo.com/it/en/women/featured/eco-apparel/"],
        ["Женщины меринос", "Женщины рекомендуемое", 3, "https://www.odlo.com/it/en/women/featured/merino/"],
        ["Женщины бег по тропе", "Женщины рекомендуемое", 3, "https://www.odlo.com/it/en/women/featured/trail-running/"],
        ["Женщины Active 365", "Женщины рекомендуемое", 3, "https://www.odlo.com/it/en/women/featured/active-365/"],
        ["Женщины Ride 365", "Женщины рекомендуемое", 3, "https://www.odlo.com/it/en/women/featured/ride-365/"],
        ["Женщины бег Zero weight", "Женщины рекомендуемое", 3, "https://www.odlo.com/it/en/women/featured/zeroweight-running/"],
        ["Женщины езда на велосипеде Zero weight", "Женщины рекомендуемое", 3, "https://www.odlo.com/it/en/women/featured/zeroweight-cycling/"],
        ["Женщины езда на горных велосипедах", "Женщины рекомендуемое", 3, "https://www.odlo.com/it/en/women/featured/mountain-biking/"],
       

        ["Мужчины"],
        
        ["Мужчины распродажа", "Мужская одежда", 2, "https://www.odlo.com/it/en/men/sale/"],

        ["Мужская одежда", "Мужчины"],
        ["Мужчины нижние слои (куртки)", "Мужская одежда", 3, "https://www.odlo.com/it/en/men/apparel/base-layers/"],
        ["Мужчины нижнее белье", "Мужская одежда", 3, "https://www.odlo.com/it/en/men/apparel/underwear/"],
        ["Мужчины футболки и поло", "Мужская одежда", 3, "https://www.odlo.com/it/en/men/apparel/t-shirts-polos/"],
        ["Мужчины шорты", "Мужская одежда", 3, "https://www.odlo.com/it/en/men/apparel/shorts/"],
        ["Мужчины брюки и колготки", "Мужская одежда", 3, "https://www.odlo.com/it/en/men/apparel/pants-tights/"],
        ["Мужчины средние слои (куртки) и длинные рукава", "Мужская одежда", 3, "https://www.odlo.com/it/en/men/apparel/mid-layers-longsleeves/"],
        ["Мужчины куртки и жилеты", "Мужская одежда", 3, "https://www.odlo.com/it/en/men/apparel/jackets-vests/"],
        ["Мужчины носки", "Мужская одежда", 3, "https://www.odlo.com/it/en/men/apparel/socks/"],
        ["Мужчины головные уборы и перчатки", "Мужская одежда", 3, "https://www.odlo.com/it/en/men/apparel/headwear-gloves/"],
        ["Мужчины другие аксессуары", "Мужская одежда", 3, "https://www.odlo.com/it/en/men/apparel/other-accessories/"],
        
        ["Мужчины спорт", "Мужчины"],
        ["Мужчины бег", "Мужчины спорт", 3, "https://www.odlo.com/it/en/men/sports/running/"],
        ["Мужчины тренировки", "Мужчины спорт", 3, "https://www.odlo.com/it/en/men/sports/training/"],
        ["Мужчины езда на велосипеде", "Мужчины спорт", 3, "https://www.odlo.com/it/en/men/sports/cycling/"],
        ["Мужчины пеший туризм", "Мужчины спорт", 3, "https://www.odlo.com/it/en/men/sports/hiking/"],
        ["Мужчины Everyday 365", "Мужчины спорт", 3, "https://www.odlo.com/it/en/men/sports/everyday-365/"],
        ["Мужчины лыжи и снег", "Мужчины спорт", 3, "https://www.odlo.com/it/en/men/sports/ski-snow/"],
        ["Мужчины катание на беговых лыжах", "Мужчины спорт", 3, "https://www.odlo.com/it/en/men/sports/ski-snow/"],

        ["Мужчины технологии", "Мужчины"],
        ["Мужчины Active Spine", "Мужчины технологии", 3, "https://www.odlo.com/it/en/men/technologies/active-spine/"],
        ["Мужчины Dual Dry", "Мужчины технологии", 3, "https://www.odlo.com/it/en/men/technologies/dual-dry/"],
        ["Мужчины Chill-Tec", "Мужчины технологии", 3, "https://www.odlo.com/it/en/men/technologies/chill-tec/"],
        ["Мужчины F-Dry", "Мужчины технологии", 3, "https://www.odlo.com/it/en/men/technologies/f-dry/"],
        ["Мужчины Ceramicool", "Мужчины технологии", 3, "https://www.odlo.com/it/en/men/technologies/ceramicool/"],
        ["Мужчины Linencool", "Мужчины технологии", 3, "https://www.odlo.com/it/en/men/technologies/linencool/"],
        ["Мужчины Performance wool", "Мужчины технологии", 3, "https://www.odlo.com/it/en/men/technologies/performance-wool/"],
        ["Мужчины ZeroScent", "Мужчины технологии", 3, "https://www.odlo.com/it/en/men/technologies/zeroscent/"],
        
        ["Мужчины рекомендуемое", "Мужчины"],
        ["Мужчины бестселлеры", "Мужчины рекомендуемое", 3, "https://www.odlo.com/it/en/men/featured/bestsellers/"],
        ["Мужчины гид по нижнему слою (куртки)", "Мужчины рекомендуемое", 3, "https://www.odlo.com/it/en/men/featured/base-layer-guide/"],
        ["Мужчины экологичная одежда", "Мужчины рекомендуемое", 3, "https://www.odlo.com/it/en/men/apparel/t-shirts-polos/"],
        ["Мужчины меринос", "Мужчины рекомендуемое", 3, "https://www.odlo.com/it/en/men/featured/merino/"],
        ["Мужчины бег по тропе", "Мужчины рекомендуемое", 3, "https://www.odlo.com/it/en/men/featured/trail-running/"],
        ["Мужчины Active 365", "Мужчины рекомендуемое", 3, "https://www.odlo.com/it/en/men/featured/active-365/"],
        ["Мужчины Ride 365", "Мужчины рекомендуемое", 3, "https://www.odlo.com/it/en/men/featured/ride-365/"],
        ["Мужчины бег Zero weight", "Мужчины рекомендуемое", 3, "https://www.odlo.com/it/en/men/featured/ride-365/"],
        ["Мужчины езда на велосипеде Zero weight", "Мужчины рекомендуемое", 3, "https://www.odlo.com/it/en/men/featured/zeroweight-cycling/"],
        ["Мужчины езда на горных велосипедах", "Мужчины рекомендуемое", 3, "https://www.odlo.com/it/en/men/featured/mountain-biking/"],


        ["Дети"],
        
        ["Товары", "Дети"],
        ["Детская одежда", "Товары", 3, "https://www.odlo.com/it/en/kids/products/clothing/"],
        ["Дети аксессуары", "Товары", 3, "https://www.odlo.com/it/en/kids/products/accessories/"],
        ["Игры на природе", "Товары", 3, "https://www.odlo.com/it/en/kids/products/play-in-natural/"],
        
        ["Дети спорт", "Дети"],
        ["Пешие прогулки и отдых на свежем воздухе", "Дети спорт", 3, "https://www.odlo.com/it/en/kids/sports/hiking-outdoor/"],
        ["Лыжи и снег", "Дети спорт", 3, "https://www.odlo.com/it/en/kids/sports/hiking-outdoor/"],
        
        ["Распродажа Дети", "Дети", 2, "https://www.odlo.com/it/en/kids/sale/"],     
    ]
    items = []

    async with aiohttp.ClientSession(headers=headers, trust_env=True) as session:
        #auth
        test_link = "https://www.odlo.com/it/en/women/apparel/headwear-gloves/"
        async with session.get(test_link, ssl=False) as response:
            webpage = await response.text()
            
        dialogue_window_url = "https://www.odlo.com/on/demandware.store/Sites-odlo-eu-Site/en_IT/Country-GetChangeForm?format=ajax"
        async with session.get(dialogue_window_url, ssl=False) as response:
            webpage = await response.text()
        
        url_to_set_settings = "https://www.odlo.com/on/demandware.store/Sites-odlo-eu-Site/en_IT/Country-Change"
        async with session.post(url_to_set_settings, data=data, ssl=False) as response:
            webpage = await response.text() 

        for subcategory in SUBCATEGORIES:
            logging.info(f'Starting {CAT_NAME}: {subcategory[0]}')
            try:
                category_url = subcategory[-1]
                async with session.get(category_url, ssl=False) as response:
                    webpage = await response.text()
                with open("site.html", "w", encoding="utf-8") as file:
                    file.write(webpage)
                soup = bs(webpage, "html.parser")
                product_urls = [i.find("a").get("href") for i in soup.find("div", attrs={"id" : "search-result-items"}).find_all("div", attrs={"class" : "l-plp-grid__item"})]
                print(product_urls)
                for product_url in product_urls:
                    try:
                        await asyncio.sleep(2)
                        async with session.get(product_url, ssl=False) as response:
                            webpage = await response.text()
                        soup = bs(webpage, "html.parser")
                        article = product_url.split("?")[-1].strip(" \n\r")
                        try:
                            title = soup.find("h1").getText().strip(" \n\r")
                        except Exception as err:
                            print(err)
                            title = None
                            
                        try:
                            current_price = int((float(soup.find('span', attrs={"class" : "product-price__item m-new"}).text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                            old_price = int((float(soup.find('span', attrs={"class" : "product-price__item m-old"}).text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                        except:
                            old_price = None
                            try:
                                current_price = int((float(soup.find('span', attrs={"class" : "product-price__item m-usual"}).text.strip(' ').strip('\n').strip(' ').strip('€').replace(',', '.')) * (EURO_COSTS + 1)))
                            except:
                                current_price = None
                        
                        #try:
                        #    description = soup.find("div", attrs={"class" : "promo-article__content"}).getText().strip("\n\r ,")[:700]
                        #except:
                        description = ""
                        
                        if old_price:
                            percent = int(100 - float(current_price) / (float(old_price) / 100))
                            description = description[:700] + f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                        
                        try:
                            image_links = []
                            image_links.append(soup.find("img", attrs={"class" : "primary-image"}).get("src"))
                            for image in soup.find("div", attrs={"class" : "thumbnail-items"}).find_all("img"):
                                try:
                                    data = json.loads(image.get("data-lgimg"))
                                    image_links.append(data["url"])
                                except:
                                    pass
                        except Exception as err:
                            print(err)
                            pass
                        try:
                            panel = soup.find("div", attrs={"class" : "filters-tabs-sizes"})
                            sizes = []
                            for span in panel.find_all("span"):
                                sizes.append(span.getText().strip(" \n\r"))
                            if len(sizes) > 0:
                                sizes = ", ".join(sizes)
                                description += '\n\nРазмеры:\n' + sizes
                        except:
                            pass
                        
                        if not os.path.exists(f"database/images/{CAT_NAME}"):
                            os.mkdir(f"database/images/{CAT_NAME}")

                        if not os.path.exists(f"database/images/{CAT_NAME}/{subcategory[0]}"):
                            os.mkdir(f"database/images/{CAT_NAME}/{subcategory[0]}")
                        
                        i = product_urls.index(product_url) + 1
                        images = ''
                        
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
                            except:
                                continue
                        item = [title, description, current_price, image_links, sizes, article, product_url]
                        print(item)
                        items.append(item)
                        
                    except Exception as ex:
                        logging.warning(f'{CAT_NAME} pr - {ex}')
            except:
                pass
                    
                        
                        


if __name__ == "__main__":
    asyncio.run(get_odlo())