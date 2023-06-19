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
        ["Куртки для яхтинга мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/sailing-jackets"],
        ["Ветровки мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/shell-jackets"],
        ["Туристические куртки мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/mountain-hiking-jackets"],
        ["Дождевики мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/rain-jackets"],
        ["Жилеты мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/vest"],
        ["Повседневные куртки мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/casual-jackets"],
        ["Ветровки мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/windbreakers"],
        ["Пуховики мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/down-jackets"],
        ["Парки мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/parka"],
        ["Зимние куртки мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/winter-jackets"],
        ["Лыжные куртки мужские", "Верхний слой (куртки) для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/jackets/ski-jackets"],

        ["Средний слой для мужчин", "Мужчины", 2],
        ["Флис мужской", "Средний слой для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/midlayers/fleece"],
        ["Активный промежуточный слой для мужчин", "Средний слой для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/midlayers/active-midlayers"],
        ["Изолированный промежуточный слой для мужчин", "Средний слой для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/midlayers/insulated-midlayers"],

        ["Брюки мужские", "Мужчины", 2],
        ["Штаны для яхтинга мужские", "Брюки мужские", 3, "https://www.hellyhansen.com/en_it/mens/pants/sailing-pants"],
        ["Брюки-ракушки мужские", "Брюки мужские", 3, "https://www.hellyhansen.com/en_it/mens/pants/shell-pants"],
        ["Походные штаны мужские", "Брюки мужские", 3, "https://www.hellyhansen.com/en_it/mens/pants/mountain-hiking-pants"],
        ["Брюки от дождя мужские", "Брюки мужские", 3, "https://www.hellyhansen.com/en_it/mens/pants/waterproof-pants"],
        ["Шорты мужские", "Брюки мужские", 3, "https://www.hellyhansen.com/en_it/mens/pants/shorts"],
        ["Повседневные брюки мужские", "Брюки мужские", 3, "https://www.hellyhansen.com/en_it/mens/pants/casual-pants"],
        ["Лыжные штаны мужские", "Брюки мужские", 3, "https://www.hellyhansen.com/en_it/mens/pants/ski-pants"],

        ["Топы мужские", "Мужчины", 2],
        ["Толстовки и кофты мужские", "Топы мужские", 3, "https://www.hellyhansen.com/en_it/mens/tops/hoodies"],
        ["Свитера мужские", "Топы мужские", 3, "https://www.hellyhansen.com/en_it/mens/tops/sweaters-knits"],
        ["Футболки мужские", "Топы мужские", 3, "https://www.hellyhansen.com/en_it/mens/tops/t-shirts"],
        ["Поло мужские", "Топы мужские", 3, "https://www.hellyhansen.com/en_it/mens/tops/polos"],
        ["Рубашки мужские", "Топы мужские", 3, "https://www.hellyhansen.com/en_it/mens/tops/shirts"],

        ["Нижний слой для мужчин", "Мужчины", 2],
        ["Активный нижний слой для мужчин", "Нижний слой для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/base-layer/active-base-layers"],
        ["Нижний слой Solen UPF для мужчин", "Нижний слой для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/base-layer/solen"],
        ["Нижний слой из мериносовой шерсти для мужчин", "Нижний слой для мужчин", 3, "https://www.hellyhansen.com/en_it/mens/base-layer/merino-wool-base-layers"],

        ["Обувь мужская", "Мужчины", 2],
        ["Обувь для яхтинга мужская", "Обувь мужская", 3, "https://www.hellyhansen.com/en_it/mens/footwear/sailing-watersports"],
        ["Походная обувь мужская", "Обувь мужская", 3, "https://www.hellyhansen.com/en_it/mens/footwear/trail-hiking"],
        ["Повседневная обувь и кроссовки мужские", "Обувь мужская", 3, "https://www.hellyhansen.com/en_it/mens/footwear/casual-shoes"],
        ["Сандалии и тапочки мужские", "Обувь мужская", 3, "https://www.hellyhansen.com/en_it/mens/footwear/sandals-slippers"],
        ["Резиновые сапоги мужские", "Обувь мужская", 3, "https://www.hellyhansen.com/en_it/mens/footwear/rubber-boots"],
        ["Зимние ботинки мужские", "Обувь мужская", 3, "https://www.hellyhansen.com/en_it/mens/footwear/winter-boots"],

        ["Аксессуары мужские", "Мужчины", 2],
        ["Плавки мужские", "Аксессуары мужские", 3, "https://www.hellyhansen.com/en_it/mens/accessories/beach-swimwear"],
        ["Головные уборы мужские", "Аксессуары мужские", 3, "https://www.hellyhansen.com/en_it/mens/accessories/hats-beanies-caps"],
        ["Носки мужские", "Аксессуары мужские", 3, "https://www.hellyhansen.com/en_it/mens/accessories/socks"],
        ["Боксеры мужские", "Аксессуары мужские", 3, "https://www.hellyhansen.com/en_it/mens/accessories/boxer-brief"],
        ["Перчатки и варежки мужские", "Аксессуары мужские", 3, "https://www.hellyhansen.com/en_it/mens/accessories/gloves-mittens"],
        ["Грелки для шеи мужские", "Аксессуары мужские", 3, "https://www.hellyhansen.com/en_it/mens/accessories/neck-warmers"],

        # ["Новые поступления для мужчин", "Мужчины", 2, "https://www.hellyhansen.com/en_it/mens/new-arrivals"],
        # ["Парусный спорт для мужчин", "Новые поступления для мужчин", 3, "https://www.hellyhansen.com/en_it/shop/new-arrivals/sailing/men"],
        # ["На открытом воздухе для мужчин", "Новые поступления для мужчин", 3, "https://www.hellyhansen.com/en_it/shop/new-arrivals/outdoor/men"],
        # ["Образ жизни для мужчин", "Новые поступления для мужчин", 3, "https://www.hellyhansen.com/en_it/shop/new-arrivals/lifestyle/men"],

        # ["Магазин по активным занятиям для мужчин", "Мужчины", 2],
        # ["Парусный спорт для мужчин", "Магазин по деятельности для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/sailing/men"],
        # ["На открытом воздухе для мужчин", "Магазин по деятельности для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/men"],
        # ["Образ жизни для мужчин", "Магазин по деятельности для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/urban/men"],
        # ["Горнолыжный спорт для мужчин", "Магазин по деятельности для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/skiing/men"],

        # ["Избранные коллекции для мужчин", "Мужчины", 2],
        # ["Солнцезащитная одежда для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/shop/sun-protective-clothing/men"],
        # ["Гонка за океаном для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/sailing/the-ocean-race/men"],
        # ["Основы парусного спорта для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/sailing/sailing-essentials/men"],
        # ["Коллекция гидроэнергетики для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/sailing/hydropower/men"],
        # ["Коллекция горы Одина для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/odin/men"],
        # ["Верглас для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/verglas/men"],
        # ["Трейловый бег для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/trail-running/men"],
        # ["Дневные поездки для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/daytrips/men"],
        # ["Фьорд Тиль Фьель для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/fjord-til-fjell/men"],
        # ["Комфортная классика для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/urban/comfortable-classics/men"],
        # ["Непромокаемая одежда для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hellyhansen.com/en_it/activity/urban/rainwear/men/"],
        # ["Рабочая одежда для мужчин", "Избранные коллекции для мужчин", 3, "https://www.hhworkwear.com/men"],
        
        
        ["Женщины"],
        
        ["Верхний слой (куртки) для женщин", "Женщины", 2],
        ["Куртки для яхтинга женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/sailing-jackets"],
        ["Ветровки женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/shell-jackets"],
        ["Туристические куртки женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/mountain-hiking-jackets"],
        ["Дождевики женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/rain-jackets"],
        ["Жилеты женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/vest"],
        ["Повседневные куртки женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/casual-jackets"],
        ["Ветровки женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/windbreakers"],
        ["Пуховики женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/down-jackets"],
        ["Парки женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/parka"],
        ["Зимние куртки женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/winter-jackets"],
        ["Лыжные куртки женские", "Верхний слой (куртки) для женщин", 3, "https://www.hellyhansen.com/en_it/women/jackets/ski-jackets"],

        ["Средний слой для женщин", "Женщины", 2],
        ["Флис для женщин", "Средний слой для женщин", 3, "https://www.hellyhansen.com/en_it/women/midlayers/fleece"],
        ["Активный промежуточный слой для женщин", "Средний слой для женщин", 3, "https://www.hellyhansen.com/en_it/women/midlayers/active-midlayers"],
        ["Изолированный средний слои для женщин", "Средний слой для женщин", 3, "https://www.hellyhansen.com/en_it/women/midlayers/insulated-midlayers"],

        ["Брюки женские", "Женщины", 2],
        ["Штаны для яхтинга женские", "Брюки женские", 3, "https://www.hellyhansen.com/en_it/women/pants/sailing-pants"],
        ["Брюки-ракушки женские", "Брюки женские", 3, "https://www.hellyhansen.com/en_it/women/pants/shell-pants"],
        ["Походные штаны женские", "Брюки женские", 3, "https://www.hellyhansen.com/en_it/women/pants/mountain-hiking-pants"],
        ["Брюки от дождя женские", "Брюки женские", 3, "https://www.hellyhansen.com/en_it/women/pants/waterproof-pants"],
        ["Шорты женские", "Брюки женские", 3, "https://www.hellyhansen.com/en_it/women/pants/shorts"],
        ["Повседневные брюки женские", "Брюки женские", 3, "https://www.hellyhansen.com/en_it/women/pants/casual-pants"],
        ["Лыжные штаны женские", "Брюки женские", 3, "https://www.hellyhansen.com/en_it/women/pants/ski-pants"],

        ["Топы женские", "Женщины", 2],
        ["Толстовки и кофты женские", "Топы женские", 3, "https://www.hellyhansen.com/en_it/women/tops/hoodies"],
        ["Свитера женские", "Топы женские", 3, "https://www.hellyhansen.com/en_it/women/tops/sweaters-knits"],
        ["Футболки женские", "Топы женские", 3, "https://www.hellyhansen.com/en_it/women/tops/t-shirts"],
        ["Поло женские", "Топы женские", 3, "https://www.hellyhansen.com/en_it/women/tops/polos"],
        ["Рубашки женские", "Топы женские", 3, "https://www.hellyhansen.com/en_it/women/tops/shirts"],

        ["Нижний слой для женщин", "Женщины", 2],
        ["Активный нижний слои для женщин", "Нижний слой для женщин", 3, "https://www.hellyhansen.com/en_it/women/base-layer/active-base-layers"],
        ["Нижний слой Solen UPF для женщин", "Нижний слой для женщин", 3, "https://www.hellyhansen.com/en_it/women/base-layer/solen"],
        ["Нижний слой из мериносовой шерсти для женщин", "Нижний слой для женщин", 3, "https://www.hellyhansen.com/en_it/women/base-layer/merino-wool-base-layers"],

        ["Обувь женская", "Женщины", 2],
        ["Обувь для яхтинга", "Обувь женская", 3, "https://www.hellyhansen.com/en_it/women/footwear/sailing-watersports"],
        ["Походная обувь женская", "Обувь женская", 3, "https://www.hellyhansen.com/en_it/women/footwear/trail-hiking"],
        ["Повседневная обувь и кроссовки женские", "Обувь женская", 3, "https://www.hellyhansen.com/en_it/women/footwear/casual-shoes"],
        ["Сандалии и тапочки женская", "Обувь женская", 3, "https://www.hellyhansen.com/en_it/women/footwear/sandals-slippers"],
        ["Резиновые сапоги женская", "Обувь женская", 3, "https://www.hellyhansen.com/en_it/women/footwear/rubber-boots"],
        ["Зимние ботинки женская", "Обувь женская", 3, "https://www.hellyhansen.com/en_it/women/footwear/winter-boots"],

        ["Аксессуары женские", "Женщины", 2],
        ["Купальники женские", "Аксессуары женские", 3, "https://www.hellyhansen.com/en_it/women/accessories/beach-swimwear"],
        ["Головные уборы женские", "Аксессуары женские", 3, "https://www.hellyhansen.com/en_it/women/accessories/hats-beanies-caps"],
        ["Носки женские", "Аксессуары женские", 3, "https://www.hellyhansen.com/en_it/women/accessories/socks"],
        ["Боксеры женские", "Аксессуары женские", 3, "https://www.hellyhansen.com/en_it/women/accessories/boxer-brief"],
        ["Перчатки и варежки женские", "Аксессуары женские", 3, "https://www.hellyhansen.com/en_it/women/accessories/gloves-mittens"],
        ["Грелки для шеи женские", "Аксессуары женские", 3, "https://www.hellyhansen.com/en_it/women/accessories/neck-warmers"],

        # ["Магазин по активным занятиям для женщин", "Женщины", 2],
        # ["Парусный спорт", "Магазин по деятельности для женщин", 3, "https://www.hellyhansen.com/en_it/activity/sailing/women"],
        # ["На открытом воздухе", "Магазин по деятельности для женщин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/women"],
        # ["Образ жизни", "Магазин по деятельности для женщин", 3, "https://www.hellyhansen.com/en_it/activity/urban/women"],
        # ["Горнолыжный спорт", "Магазин по деятельности для женщин", 3, "https://www.hellyhansen.com/en_it/activity/skiing/women"],

        # ["Избранные коллекции для женщин", "Женщины", 2],
        # ["Солнцезащитная одежда для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/shop/sun-protective-clothing/women"],
        # ["Гонка за океаном для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/activity/sailing/the-ocean-race/women"],
        # ["Основы парусного спорта для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/activity/sailing/sailing-essentials/women"],
        # ["Коллекция гидроэнергетики для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/activity/sailing/hydropower/women"],
        # ["Коллекция горы Одина для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/odin/women"],
        # ["Верглас для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/verglas/women"],
        # ["Трейловый бег для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/trail-running/women"],
        # ["Дневные поездки для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/daytrips/women"],
        # ["Фьорд Тиль Фьель для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/activity/outdoor/fjord-til-fjell/women"],
        # ["Комфортная классика для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/activity/urban/comfortable-classics/women"],
        # ["Непромокаемая одежда для женщин", "Избранные коллекции для женщин", 3, "https://www.hellyhansen.com/en_it/activity/urban/rainwear/women/"],
        
        ["Дети"],
        ["Куртки детские", "Дети", 2, "https://www.hellyhansen.com/en_it/kids-juniors/kids/jackets"],
        ["Брюки детские", "Дети", 2, "https://www.hellyhansen.com/en_it/kids-juniors/kids/pants"],
        ["Дождевики детские", "Дети", 2, "https://www.hellyhansen.com/en_it/kids-juniors/kids/rainsets"],
        ["Комбинезоны детские", "Дети", 2, "https://www.hellyhansen.com/en_it/kids-juniors/kids/playsuits"],
        ["Флис и средний слой для детей", "Дети", 2, "https://www.hellyhansen.com/en_it/kids-juniors/kids/fleece"],
        ["Нижний слой для детей", "Дети", 2, "https://www.hellyhansen.com/en_it/kids-juniors/kids/base-layers"],
        ["Топы детские", "Дети", 2, "https://www.hellyhansen.com/en_it/kids-juniors/kids/tops"],
        
        ["Подростки", "Дети", 2],
        ["Куртки для подростков", "Подростки", 3, "https://www.hellyhansen.com/en_it/kids-juniors/juniors/jackets"],
        ["Брюки для подростков", "Подростки", 3, "https://www.hellyhansen.com/en_it/kids-juniors/juniors/pants"],
        ["Флис и средний слой для подростков", "Подростки", 3, "https://www.hellyhansen.com/en_it/kids-juniors/juniors/fleece"],
        ["Базовые слои для подростков", "Подростки", 3, "https://www.hellyhansen.com/en_it/kids-juniors/juniors/base-layers"],
        ["Топы для подростков", "Подростки", 3, "https://www.hellyhansen.com/en_it/kids-juniors/juniors/tops"],
        
        ["Аксессуары детские", "Дети", 2],
        ["Обувь детская", "Аксессуары детские", 3, "https://www.hellyhansen.com/en_it/kids-juniors/accessories/shoes"],
        ["Головные уборы детские", "Аксессуары детские", 3, "https://www.hellyhansen.com/en_it/kids-juniors/accessories/hats"],
        ["Перчатки и варежки детские", "Аксессуары детские", 3, "https://www.hellyhansen.com/en_it/kids-juniors/accessories/gloves-mittens"],
        ["Носки детские", "Аксессуары детские", 3, "https://www.hellyhansen.com/en_it/kids-juniors/accessories/socks"],
        
        # ["Новые поступления для детей", "Дети", 2, "https://www.hellyhansen.com/en_it/kids-juniors/new-arrivals/kids-new-arrivals"]
        # ["Новые поступления для подростков", "Подростки", 3, "https://www.hellyhansen.com/en_it/kids-juniors/new-arrivals/juniors-new-arrivals"]

        # ["Магазин по активным занятиям для детей", "Дети", 2],
        # ["Горнолыжный спорт для детей", "Магазин по активным занятиям для детей", 3, "https://www.hellyhansen.com/en_it/kids-juniors/shop-by-activity/skiing"],
        # ["На открытом воздухе для детей", "Магазин по активным занятиям для детей", 3, "https://www.hellyhansen.com/en_it/kids-juniors/shop-by-activity/outdoor"],
        # ["Парусный спорт для детей", "Магазин по активным занятиям для детей", 3, "https://www.hellyhansen.com/en_it/kids-juniors/shop-by-activity/sailing"],

        # ["Избранные коллекции для детей", "Дети", 2],
        # ["Детская непромокаемая одежда", "Избранные коллекции для детей", 3, "https://www.hellyhansen.com/en_it/activity/urban/rainwear/kids"],
        # ["Непромокаемая одежда для подростков", "Избранные коллекции для детей", 3, "https://www.hellyhansen.com/en_it/activity/urban/rainwear/juniors"],
        # ["Для активных детей", "Избранные коллекции для детей", 3, "https://www.hellyhansen.com/en_it/kids-juniors/shop-by/active-kids"],


        ["Экипировка"],
        ["Сумки", "Экипировка", 2],
        ["Спортивные сумки", "Сумки", 3, "https://www.hellyhansen.com/en_it/gear/bags/duffel-bags"],
        ["Тележки и чемоданы на колесах", "Сумки", 3, "https://www.hellyhansen.com/en_it/gear/bags/trolleys-rolling-luggage"],
        ["Водонепроницаемые мешки", "Сумки", 3, "https://www.hellyhansen.com/en_it/gear/bags/dry-bags"],
        ["Аксессуары для путешествий", "Сумки", 3, "https://www.hellyhansen.com/en_it/gear/bags/travel-accessories"],
        ["Слинги и поясные сумки", "Сумки", 3, "https://www.hellyhansen.com/en_it/gear/bags/slings-waist-bags"],

        ["Рюкзаки", "Экипировка", 2],
        ["Походные рюкзаки", "Рюкзаки", 2, "https://www.hellyhansen.com/en_it/gear/backpacks/outdoor-backpacks"],
        ["Повседневные рюкзаки", "Рюкзаки", 2, "https://www.hellyhansen.com/en_it/gear/backpacks/casual-backpacks"],

        ["Водные виды спорта", "Экипировка", 2],
        ["Спасательные жилеты", "Водные виды спорта", 3, "https://www.hellyhansen.com/en_it/gear/watersports/life-jackets"],
        ["Гидрокостюмы и парусное снаряжение", "Водные виды спорта", 3, "https://www.hellyhansen.com/en_it/gear/watersports/wet-suits"],
        ["Детские спасательные жилеты", "Водные виды спорта", 3, "https://www.hellyhansen.com/en_it/gear/watersports/kids-life-jackets"],
        ["Детали и комплекты для ремонта спасательных жилетов", "Водные виды спорта", 3, "https://www.hellyhansen.com/en_it/gear/watersports/life-jacket-parts"],

        # ["Новинки", "https://www.hellyhansen.com/en_it/shop/new-arrivals?promo_name=ss23_newarrivals&promo_id=090323&promo_creative=newarrivals&promo_position=menu"]
    
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
        base_url = subcategory[-1]
        items = []
        async with aiohttp.ClientSession(headers=HEADERS, trust_env=True) as session:
            #try:
            async with session.get(base_url, ssl=False) as response:
                webpage = await response.text()
                print(webpage)
                def extract_category_id_from_page(webpage : str) -> str:
                    match = re.search(r"id&quot;:&quot;\d{1,10}&quot;", webpage)
                    id_with_text = match[0] 
                    id = id_with_text.split("id&quot;:&quot;")[1].split("&quot;")[0]
                    return id
                
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
                    
                category_id = extract_category_id_from_page(webpage)
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
        #if not crud.subcategory_exists(name=subcategory[0], category=CAT_NAME):
        #    parent_subcategory = crud.get_subcategory(name=subcategory[1], category_id=category.id)
        #    crud.create_subcategory(name=subcategory[0], category=CAT_NAME, parent_subcategory=parent_subcategory.id, level=subcategory[2])
        #await crud.create_products(category=CAT_NAME, subcategory=subcategory[0], items=items)
    
    #await bot.send_message(227184505, f'{CAT_NAME} закончил парсинг')


