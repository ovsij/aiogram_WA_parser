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
import re
import json

async def get_hellyhansen():
    EURO_COSTS = euro_cost()
    HEADERS = {
        "Host": "www.hellyhansen.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
        "store" : "en_it"
    }
    CAT_NAME = "Hellyhansen"
    SUBCATEGORIES = [
        
        ["Мужчины"],
        ["Верхний слой (куртки) для мужчин", "Мужчины", 2],
        ["Куртки для яхтинга мужские", "Верхний слой (куртки) для мужчин", 3, "1561"],
        ["Ветровки мужские", "Верхний слой (куртки) для мужчин", 3, "295"],
        ["Туристические куртки мужские", "Верхний слой (куртки) для мужчин", 3, "1594"],
        ["Дождевики мужские", "Верхний слой (куртки) для мужчин", 3, "1588"],
        ["Жилеты мужские", "Верхний слой (куртки) для мужчин", 3, "193"],
        ["Повседневные куртки мужские", "Верхний слой (куртки) для мужчин", 3, "1591"],
        ["Ветровки мужские", "Верхний слой (куртки) для мужчин", 3, "4742"],
        ["Пуховики мужские", "Верхний слой (куртки) для мужчин", 3, "448"],
        ["Парки мужские", "Верхний слой (куртки) для мужчин", 3, "568"],
        ["Зимние куртки мужские", "Верхний слой (куртки) для мужчин", 3, "5777"],
        ["Лыжные куртки мужские", "Верхний слой (куртки) для мужчин", 3, "1567"],

        ["Средний слой для мужчин", "Мужчины", 2],
        ["Флис мужской", "Средний слой для мужчин", 3, "352"],
        ["Активный промежуточный слой для мужчин", "Средний слой для мужчин", 3, "5786"],
        ["Изолированный промежуточный слой для мужчин", "Средний слой для мужчин", 3, "2027"],

        ["Брюки мужские", "Мужчины", 2],
        ["Штаны для яхтинга мужские", "Брюки мужские", 3, "1603"],
        ["Брюки-ракушки мужские", "Брюки мужские", 3, "6198"],
        ["Походные штаны мужские", "Брюки мужские", 3, "1609"],
        ["Брюки от дождя мужские", "Брюки мужские", 3, "586"],
        ["Шорты мужские", "Брюки мужские", 3, "5783"],
        ["Повседневные брюки мужские", "Брюки мужские", 3, "5780"],
        ["Лыжные штаны мужские", "Брюки мужские", 3, "1600"],

        ["Топы мужские", "Мужчины", 2],
        ["Толстовки и кофты мужские", "Топы мужские", 3, "5068"],
        ["Свитера мужские", "Топы мужские", 3, "1549"],
        ["Футболки мужские", "Топы мужские", 3, "3342"],
        ["Поло мужские", "Топы мужские", 3, "3345"],
        ["Рубашки мужские", "Топы мужские", 3, "5789"],

        ["Нижний слой для мужчин", "Мужчины", 2],
        ["Активный нижний слой для мужчин", "Нижний слой для мужчин", 3, "5795"],
        ["Нижний слой Solen UPF для мужчин", "Нижний слой для мужчин", 3, "5107"],
        ["Нижний слой из мериносовой шерсти для мужчин", "Нижний слой для мужчин", 3, "5792"],

        ["Обувь мужская", "Мужчины", 2],
        ["Обувь для яхтинга мужская", "Обувь мужская", 3, "1702"],
        ["Походная обувь мужская", "Обувь мужская", 3, "1690"],
        ["Повседневная обувь и кроссовки мужские", "Обувь мужская", 3, "1699"],
        ["Сандалии и тапочки мужские", "Обувь мужская", 3, "5798"],
        ["Резиновые сапоги мужские", "Обувь мужская", 3, "376"],
        ["Зимние ботинки мужские", "Обувь мужская", 3, "1693"],

        ["Аксессуары мужские", "Мужчины", 2],
        ["Плавки мужские", "Аксессуары мужские", 3, "5804"],
        ["Головные уборы мужские", "Аксессуары мужские", 3, "523"],
        ["Носки мужские", "Аксессуары мужские", 3, "397"],
        ["Боксеры мужские", "Аксессуары мужские", 3, "646"],
        ["Перчатки и варежки мужские", "Аксессуары мужские", 3, "583"],
        ["Грелки для шеи мужские", "Аксессуары мужские", 3, "5801"],

        # ["Новые поступления для мужчин", "Мужчины", 2],
        # ["Парусный спорт для мужчин", "Новые поступления для мужчин", 3, "6949"],
        # ["На открытом воздухе для мужчин", "Новые поступления для мужчин", 3, "6955"],
        # ["Образ жизни для мужчин", "Новые поступления для мужчин", 3, "6961"],

        # ["Магазин по активным занятиям для мужчин", "Мужчины", 2],
        # ["Парусный спорт для мужчин", "Магазин по деятельности для мужчин", 3, "6736"],
        # ["На открытом воздухе для мужчин", "Магазин по деятельности для мужчин", 3, "6684"],
        # ["Образ жизни для мужчин", "Магазин по деятельности для мужчин", 3, "6690"],
        # ["Горнолыжный спорт для мужчин", "Магазин по деятельности для мужчин", 3, "6742"],

        # ["Избранные коллекции для мужчин", "Мужчины", 2],
        # ["Солнцезащитная одежда для мужчин", "Избранные коллекции для мужчин", 3, "7030"],
        # ["Гонка за океаном для мужчин", "Избранные коллекции для мужчин", 3, "6841"],
        # ["Основы парусного спорта для мужчин", "Избранные коллекции для мужчин", 3, "6535"],
        # ["Коллекция гидроэнергетики для мужчин", "Избранные коллекции для мужчин", 3, "6502"],
        # ["Коллекция горы Одина для мужчин", "Избранные коллекции для мужчин", 3, "6419"],
        # ["Верглас для мужчин", "Избранные коллекции для мужчин", 3, "6437"],
        # ["Трейловый бег для мужчин", "Избранные коллекции для мужчин", 3, "6411"],
        # ["Дневные поездки для мужчин", "Избранные коллекции для мужчин", 3, "6355"],
        # ["Фьорд Тиль Фьель для мужчин", "Избранные коллекции для мужчин", 3, "6428"],
        # ["Комфортная классика для мужчин", "Избранные коллекции для мужчин", 3, "6467"],
        # ["Непромокаемая одежда для мужчин", "Избранные коллекции для мужчин", 3, "4281"],
        # ["Рабочая одежда для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hhworkwear.com/men"],
        
        
        ["Женщины"],
        
        ["Верхний слой (куртки) для женщин", "Женщины", 2],
        ["Куртки для яхтинга женские", "Верхний слой (куртки) для женщин", 3, "1582"],
        ["Ветровки женские", "Верхний слой (куртки) для женщин", 3, "1642"],
        ["Туристические куртки женские", "Верхний слой (куртки) для женщин", 3, "1630"],
        ["Дождевики женские", "Верхний слой (куртки) для женщин", 3, "1645"],
        ["Жилеты женские", "Верхний слой (куртки) для женщин", 3, "1803"],
        ["Повседневные куртки женские", "Верхний слой (куртки) для женщин", 3, "1636"],
        ["Ветровки женские", "Верхний слой (куртки) для женщин", 3, "4736"],
        ["Пуховики женские", "Верхний слой (куртки) для женщин", 3, "1639"],
        ["Парки женские", "Верхний слой (куртки) для женщин", 3, "1633"],
        ["Зимние куртки женские", "Верхний слой (куртки) для женщин", 3, "5819"],
        ["Лыжные куртки женские", "Верхний слой (куртки) для женщин", 3, "1627"],

        ["Средний слой для женщин", "Женщины", 2],
        ["Флис для женщин", "Средний слой для женщин", 3, "1681"],
        ["Активный промежуточный слой для женщин", "Средний слой для женщин", 3, "5828"],
        ["Изолированный средний слои для женщин", "Средний слой для женщин", 3, "1684"],

        ["Брюки женские", "Женщины", 2],
        ["Штаны для яхтинга женские", "Брюки женские", 3, "1657"],
        ["Брюки-ракушки женские", "Брюки женские", 3, "6202"],
        ["Походные штаны женские", "Брюки женские", 3, "1663"],
        ["Брюки от дождя женские", "Брюки женские", 3, "1660"],
        ["Шорты женские", "Брюки женские", 3, "5825"],
        ["Повседневные брюки женские", "Брюки женские", 3, "5822"],
        ["Лыжные штаны женские", "Брюки женские", 3, "1654"],

        ["Топы женские", "Женщины", 2],
        ["Толстовки и кофты женские", "Топы женские", 3, "5954"],
        ["Свитера женские", "Топы женские", 3, "1624"],
        ["Футболки женские", "Топы женские", 3, "3393"],
        ["Поло женские", "Топы женские", 3, "3426"],
        ["Рубашки женские", "Топы женские", 3, "5831"],
        ["Платья женские", "Топы женские", 3, "5834"],

        ["Нижний слой для женщин", "Женщины", 2],
        ["Активный нижний слои для женщин", "Нижний слой для женщин", 3, "5840"],
        ["Нижний слой Solen UPF для женщин", "Нижний слой для женщин", 3, "5110"],
        ["Нижний слой из мериносовой шерсти для женщин", "Нижний слой для женщин", 3, "5837"],

        ["Обувь женская", "Женщины", 2],
        ["Обувь для яхтинга", "Обувь женская", 3, "1779"],
        ["Походная обувь женская", "Обувь женская", 3, "1776"],
        ["Повседневная обувь и кроссовки женские", "Обувь женская", 3, "1782"],
        ["Сандалии и тапочки женская", "Обувь женская", 3, "5843"],
        ["Резиновые сапоги женская", "Обувь женская", 3, "304"],
        ["Зимние ботинки женская", "Обувь женская", 3, "1785"],

        ["Аксессуары женские", "Женщины", 2],
        ["Купальники женские", "Аксессуары женские", 3, "5849"],
        ["Головные уборы женские", "Аксессуары женские", 3, "517"],
        ["Носки женские", "Аксессуары женские", 3, "457"],
        ["Перчатки и варежки женские", "Аксессуары женские", 3, "265"],
        ["Грелки для шеи женские", "Аксессуары женские", 3, "5846"],

        # ["Магазин по активным занятиям для женщин", "Женщины", 2],
        # ["Парусный спорт", "Магазин по деятельности для женщин", 3, "6739"],
        # ["На открытом воздухе", "Магазин по деятельности для женщин", 3, "6687"],
        # ["Образ жизни", "Магазин по деятельности для женщин", 3, "6693"],
        # ["Горнолыжный спорт", "Магазин по деятельности для женщин", 3, "6745"],

        # ["Избранные коллекции для женщин", "Женщины", 2],
        # ["Солнцезащитная одежда для женщин", "Избранные коллекции для женщин", 3, "7033"],
        # ["Гонка за океаном для женщин", "Избранные коллекции для женщин", 3, "6844"],
        # ["Основы парусного спорта для женщин", "Избранные коллекции для женщин", 3, "6538"],
        # ["Коллекция гидроэнергетики для женщин", "Избранные коллекции для женщин", 3, "6505"],
        # ["Коллекция горы Одина для женщин", "Избранные коллекции для женщин", 3, "6422"],
        # ["Верглас для женщин", "Избранные коллекции для женщин", 3, "6440"],
        # ["Трейловый бег для женщин", "Избранные коллекции для женщин", 3, "6414"],
        # ["Дневные поездки для женщин", "Избранные коллекции для женщин", 3, "6358"],
        # ["Фьорд Тиль Фьель для женщин", "Избранные коллекции для женщин", 3, "6431"],
        # ["Комфортная классика для женщин", "Избранные коллекции для женщин", 3, "6470"],
        # ["Непромокаемая одежда для женщин", "Избранные коллекции для женщин", 3, "4284"],
        
        ["Дети"],
        ["Куртки детские", "Дети", 2, "6042"],
        ["Брюки детские", "Дети", 2, "6045"],
        ["Дождевики детские", "Дети", 2, "6048"],
        ["Комбинезоны детские", "Дети", 2, "6051"],
        ["Флис и средний слой для детей", "Дети", 2, "6054"],
        ["Нижний слой для детей", "Дети", 2, "6057"],
        ["Топы детские", "Дети", 2, "6060"],
        
        ["Подростки", "Дети", 2],
        ["Куртки для подростков", "Подростки", 3, "6066"],
        ["Брюки для подростков", "Подростки", 3, "6069"],
        ["Флис и средний слой для подростков", "Подростки", 3, "6072"],
        ["Базовые слои для подростков", "Подростки", 3, "6075"],
        ["Топы для подростков", "Подростки", 3, "6078"],
        
        ["Аксессуары детские", "Дети", 2],
        ["Обувь детская", "Аксессуары детские", 3, "6084"],
        ["Головные уборы детские", "Аксессуары детские", 3, "6090"],
        ["Перчатки и варежки детские", "Аксессуары детские", 3, "6093"],
        ["Носки детские", "Аксессуары детские", 3, "6096"],
        
        # ["Новые поступления для детей", "Дети", 2, "6102"]
        # ["Новые поступления для подростков", "Подростки", 3, "6105"]

        # ["Магазин по активным занятиям для детей", "Дети", 2],
        # ["Горнолыжный спорт для детей", "Магазин по активным занятиям для детей", 3, "6126"],
        # ["На открытом воздухе для детей", "Магазин по активным занятиям для детей", 3, "6129"],
        # ["Парусный спорт для детей", "Магазин по активным занятиям для детей", 3, "6132"],

        # ["Избранные коллекции для детей", "Дети", 2],
        # ["Детская непромокаемая одежда", "Избранные коллекции для детей", 3, "4296"],
        # ["Непромокаемая одежда для подростков", "Избранные коллекции для детей", 3, "6398"],
        # ["Для активных детей", "Избранные коллекции для детей", 3, "6319"],


        ["Экипировка"],
        ["Сумки", "Экипировка", 2],
        ["Спортивные сумки", "Сумки", 3, "5915"],
        ["Тележки и чемоданы на колесах", "Сумки", 3, "5918"],
        ["Водонепроницаемые мешки", "Сумки", 3, "5921"],
        ["Аксессуары для путешествий", "Сумки", 3, "5924"],
        ["Слинги и поясные сумки", "Сумки", 3, "5927"],

        ["Рюкзаки", "Экипировка", 2],
        ["Походные рюкзаки", "Рюкзаки", 2, "5933"],
        ["Повседневные рюкзаки", "Рюкзаки", 2, "5936"],

        ["Водные виды спорта", "Экипировка", 2],
        ["Спасательные жилеты", "Водные виды спорта", 3, "5942"],
        ["Гидрокостюмы и парусное снаряжение", "Водные виды спорта", 3, "5945"],
        ["Детские спасательные жилеты", "Водные виды спорта", 3, "5951"],
        ["Детали и комплекты для ремонта спасательных жилетов", "Водные виды спорта", 3, "5948"],

        # ["Новинки", "4061"]
    
    ]
    #category = crud.get_category(name=CAT_NAME, metacategory=crud.get_metacategory(name='Спортивные товары').id)
    
    print(len(SUBCATEGORIES))
    for subcategory in SUBCATEGORIES:
        
        #if not str(subcategory[-1]).startswith('http'):
        #    if len(subcategory) == 1:
        #        crud.create_subcategory(name=subcategory[0], category=CAT_NAME) if not crud.subcategory_exists(name=subcategory[0], category=CAT_NAME) else 0
        #    else:
        #        if not crud.subcategory_exists(name=subcategory[0], category=CAT_NAME):
        #            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=category.id)
        #            crud.create_subcategory(name=subcategory[0], category=CAT_NAME, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        #    continue
        logging.info(f'Starting {CAT_NAME}: {subcategory[0]}')
        items = []
        async with aiohttp.ClientSession(headers=HEADERS, trust_env=True) as session:
            #try:
            #print(webpage)
            
            def extract_product_keys_from_json(json_ : dict) -> list:
                try:
                    items = json_["data"]["products"]["items"]
                    product_urls = []
                    for product in items:
                        key = product["url_key"]
                        product_urls.append(key)
                    return product_urls
                except:
                    return []
                
            def does_json_contain_errors(json_ : dict) -> bool:
                try:
                    errors = json_["errors"]
                    return True
                except:
                    return False
                
            category_id = subcategory[-1]
            page_counter = 1
            url_pattern = 'https://www.hellyhansen.com/graphql?query=query GetCategoryProducts($pageSize:Int!$currentPage:Int!$filters:ProductAttributeFilterInput!$sort:ProductAttributeSortInput){products(pageSize:$pageSize currentPage:$currentPage filter:$filters sort:$sort){...ProductsFragment __typename}}fragment ProductsFragment on Products{items{id uid name price{regularPrice{amount{currency value __typename}__typename}__typename}price_range{maximum_price{final_price{value currency __typename}regular_price{value currency __typename}discount{amount_off __typename}__typename}minimum_price{final_price{value currency __typename}regular_price{value currency __typename}discount{amount_off __typename}__typename}__typename}special_price sku small_image{url __typename}image{url __typename}thumbnail{url __typename}categories{id uid name __typename}stock_status type_id url_key url_suffix __typename}aggregations{attribute_code options{value __typename}__typename}page_info{total_pages __typename}total_count __typename}&operationName=GetCategoryProducts&variables={"currentPage":current_page_value,"filters":{"category_id":{"eq":"id_tag$"}},"id":id_tag$,"pageSize":16,"sort":{"position":"ASC"}}'
            product_keys = []
            while True:
                await asyncio.sleep(3)
                products_url = url_pattern.replace("id_tag$", category_id).replace("current_page_value", str(page_counter))
                async with session.get(products_url, ssl=False) as response:
                    json_string = await response.text()
                    json_ = json.loads(json_string)
                    if does_json_contain_errors(json_):
                        break
                    product_keys += extract_product_keys_from_json(json_)
                    page_counter += 1
                    
                    
            def get_product_json_url(product_key : str) -> str:
                product_url_pattern = 'https://www.hellyhansen.com/graphql?query=query getProductSwatchesForProductPage($urlKey:String!){products(filter:{url_key:{eq:$urlKey}}){items{id uid price_range{maximum_price{final_price{value currency __typename}regular_price{value currency __typename}discount{amount_off __typename}__typename}minimum_price{final_price{value currency __typename}regular_price{value currency __typename}discount{amount_off __typename}__typename}__typename}name sku __typename ...ProductSwatchesFragment}__typename}}fragment ProductSwatchesFragment on ProductInterface{...on ConfigurableProduct{configurable_options{attribute_code attribute_id id label values{uid default_label label store_label use_default_value value_index swatch_data{...on ImageSwatchData{thumbnail __typename}value __typename}__typename}__typename}variants{attributes{code value_index uid __typename}product{id uid only_x_left_in_stock media_gallery_entries{id uid disabled file label position media_type video_content{media_type video_provider video_url video_title video_description video_metadata __typename}__typename}name sku stock_status special_price price_range{maximum_price{final_price{value currency __typename}regular_price{value currency __typename}discount{amount_off __typename}__typename}minimum_price{final_price{value currency __typename}regular_price{value currency __typename}discount{amount_off __typename}__typename}__typename}__typename}__typename}__typename}__typename}&operationName=getProductSwatchesForProductPage&variables={"urlKey":"urlKey$"}'
                result = product_url_pattern.replace("urlKey$", product_key)
                return result

            def get_url_of_json_with_description(product_key : str) -> str:
                product_url_pattern = 'https://www.hellyhansen.com/graphql?query=query getProductDetailForProductPage($urlKey:String!){products(filter:{url_key:{eq:$urlKey}}){items{id uid page_title __typename ...ProductDetailsFragment ...ProductPerformanceFragment ...ProductInfoFragment}__typename}}fragment ProductDetailsFragment on ProductInterface{__typename features short_description{html __typename}categories{id uid breadcrumbs{category_id category_name __typename}use_as_related_category name url_path __typename}description{html __typename}id uid meta_description meta_keyword name price{regularPrice{amount{currency value __typename}__typename}__typename}price_range{maximum_price{final_price{value currency __typename}regular_price{value currency __typename}discount{amount_off __typename}__typename}minimum_price{final_price{value currency __typename}regular_price{value currency __typename}discount{amount_off __typename}__typename}__typename}robots_meta_tag sku small_image{url __typename}stock_status pdf_sheet product_use_for{code title __typename}url_key}fragment ProductPerformanceFragment on ProductInterface{performance_breathability{label value __typename}performance_durability{label value __typename}performance_insulation{label value __typename}performance_waterproof{label value __typename}performance_weight{label value __typename}performance_windproof{label value __typename}product_workwear_features __typename}fragment ProductInfoFragment on ProductInterface{care_instructions{html __typename}fiber{html __typename}water_column weight_with_unit __typename}&operationName=getProductDetailForProductPage&variables={"urlKey":"urlKey$"}'
                result = product_url_pattern.replace("urlKey$", product_key)
                return result

            for product_key in product_keys:
                print(product_key)
                await asyncio.sleep(3)
                json_url = get_product_json_url(product_key)
                async with session.get(json_url, ssl = False) as response:
                    webpage = await response.text()
                    json_ = json.loads(webpage)
                    with open("js.json", "w", encoding="utf-8") as file:
                        file.write(webpage)
                    await asyncio.sleep(3)
                    article = str(product_key)
                    description = ""
                    product_data = json_["data"]["products"]["items"][0]

                    try:
                        prices = product_data["variants"][0]["product"]["price_range"]["maximum_price"]
                        current_price = int(prices["final_price"]["value"] * (EURO_COSTS + 1) * float(f"1.{crud.get_category(name=CAT_NAME).margin}"))
                        old_price = int(prices["regular_price"]["value"]  * (EURO_COSTS + 1) * float(f"1.{crud.get_category(name=CAT_NAME).margin}"))
                        if old_price - current_price != 0:
                            percent = int(100 - float(current_price) / (float(old_price) / 100))
                            description += f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб.'
                    except Exception as err:
                        print(err)
                        pass

                    try:
                        sizes = []
                        product_config : list = product_data["configurable_options"]
                        
                        for param in product_config:
                            if param["attribute_code"] == "size":
                                values = param["values"]
                                
                                for i in values:
                                    sizes.append(i["label"])
                                if len(sizes) != 0:
                                    sizes = ", ".join(sizes)
                                    description += '\n\nРазмеры:\n' + sizes
                    except Exception as err:
                        print(err)
                    
                    try:
                        image_links = []
                        product = product_data["variants"][0]["product"] 
                        for media in product["media_gallery_entries"]:
                            if media["media_type"] == "image":
                                base_image_url = "https://www.hellyhansen.com/media/catalog/product"
                                image_links.append(base_image_url + media["file"])
                    except:
                        image_links = []
                    
                #second butch of params
                json_url = get_url_of_json_with_description(product_key)
                async with session.get(json_url, ssl = False) as response:
                    webpage = await response.text()
                    json_ = json.loads(webpage)
                
                    product = json_["data"]["products"]["items"][0]
                    
                    try:
                        title = product["page_title"]
                    except Exception as err:
                        print(err)
                        title = ""  
                    try:
                        product_short_description = product["short_description"]["html"]
                        description = product_short_description + description
                    except Exception as err:
                        print(err)
                
                if not os.path.exists(f"database/images/{CAT_NAME}"):
                    os.mkdir(f"database/images/{CAT_NAME}")

                if not os.path.exists(f"database/images/{CAT_NAME}/{subcategory[0]}"):
                    os.mkdir(f"database/images/{CAT_NAME}/{subcategory[0]}")

                i = product_keys.index(product_key) + 1
                images = ''
                for link in image_links[:10]:
                    try:
                        num = image_links.index(link) + 1
                        img_path = f"database/images/{CAT_NAME}/{subcategory[0]}/{i}_{title.replace(' ', '_').replace('/', '_').replace('|', '')}_{num}.jpg"
                        if not os.path.exists(img_path):
                            async with session.get(link, ssl=False) as response:
                                f = await aiofiles.open(img_path, mode='wb')
                                await f.write(await response.read())
                                await f.close()
                        images += img_path + '\n'
                    except Exception as err:
                        print(err)
                        
                product_url = "https://www.hellyhansen.com/en_it/" + product_key
                item = [title, description, current_price, images, sizes, article, product_url]
                print(item)
                items.append(item)
            await asyncio.sleep(10)                      
            #except Exception as err:
            #    print(err)
            #    pass

        ## добавляем товары
        if not crud.subcategory_exists(name=subcategory[0], category=CAT_NAME):
            parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=category.id)
            crud.create_subcategory(name=subcategory[0], category=CAT_NAME, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        await crud.create_products(category=CAT_NAME, subcategory=subcategory[0], items=items)
    
    #await bot.send_message(227184505, f'{CAT_NAME} закончил парсинг')


