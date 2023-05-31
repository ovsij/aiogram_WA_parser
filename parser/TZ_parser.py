"""
Requirements:
python==3.10

beautifulsoup4==4.11.2
aiohttp
aiofiles==23.1.0

"""

#1. Собрать названия подкатегорий в список списков (на русском языке)
#подкатегории отличаются по уровню
#сначала обозначается подкатегория верхнего уровня, например ['Мужчины']
#затем подкатегория, которая входит в эту ['Одежда мужская', 'Мужчины', 2]
#первый элемент в списке - название подкатегории, второй - название подкатегории в которую входит эта подкатегория, третий - уровень подкатегории
#далее может быть подкатегория ['Футболки мужские', 'Одежда мужская', 3, {ссылка по которой будет проходить парсинг}]
#ВАЖНО! Все подкатегории должны иметь уникальные имена. Это решается тем, что ко всем мужским в конце добавляется "мужская/ие" к женским и детским так же
#если это аутлет, то "Футболки мужские аутет" добавляется слово аутлет

#2. Оформить все в одну асинхронную функцию как показано ниже. Функция возвращает список items в который входят все товары в данной
#подкатегории в формате [title, description, current_price, images, sizes, article, item_url]

#title - название товара

#description = f'\n\n<s>{old_price} руб.</s> -{percent}% {current_price} руб. \n\nРазмеры:\n {sizes}
#если у товара есть уценка, то как показано выше старая цена - процент скидки - новая цена
#если ууенки нет, то только размеры через запятую

#current_price - цена везде в долларах, мы допишем потом функцию по переводе в рубли по нужному нам курсу

#images - строка с путями изображений. Это есть в примере, просто вставляете как есть. Главное до этого собрать список url всех изображений в список

#sizes - все размеры через запятую

#article - артикул товара. Зависит от каталога. Обычно это значение можно найти в url товара. Должен быть уникален для каждого товара. 
#Если для разных цветов одинаковый - добавляем к артикулу через "-" цвет,
#Если для товара в разеле аутлет и в обычном разделе одинаковые артикулы - добавляем к артикулу аутлета "-outlet"

#item_url - ссылка на товар на сайте

# Пример функции ниже, готовы принять незначительные предложения по ее улучшению
# в примере используется парсинг непосредственно из страницы на сайте. 
# У некоторых сайтов есть возможность в разделе "посмотреть код" - "сеть" найти адреса API и делать запросы уже по ним
# тогда -1 элементом списка может быть как url так и какой-то ключ/айди который используется в апи
# обратите внимание, что в примере в обуви нет подкатегорий, тогда идет сразу ссылка и парсинг
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
        ['Женская одежда (верх)', 'Женская одежда', 3, 'https://www.underarmour.it/en-it/c/womens/clothing/tops/?start=0&sz=1000'],
        ['Женские бюстгальтеры', 'Женская одежда', 3, 'https://www.underarmour.it/en-it/c/womens/clothing/sports-bras/?start=0&sz=1000'],
        ['Женская одежда (низ)', 'Женская одежда', 3, 'https://www.underarmour.it/en-it/c/womens/clothing/bottoms/?start=0&sz=1000'],
        ['Женская верхняя одежда', 'Женская одежда', 3, 'https://www.underarmour.it/en-it/c/womens/clothing/outerwear/?start=0&sz=1000'],
        ['Женское белье', 'Женская одежда', 3, 'https://www.underarmour.it/en-it/c/womens/clothing-underwear/?start=0&sz=1000'],
        ['Женская обувь', 'Женщины', 2, 'https://www.underarmour.it/en-it/c/womens/shoes/?start=0&sz=1000'],
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
        logging.info(f'Starting {cat_name}: {subcategory[0]}')
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession(headers=headers, trust_env=True) as session:
            async with session.get(subcategory[-1], ssl=False) as response:
                webpage = await response.text()
                soup = bs(webpage, 'html.parser')
                item_urls = [{'title' : item.text, 'url': 'https://www.underarmour.it' + item.get('href')} for item in soup.find_all('a', 'b-tile-name')]
            items = []
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
                        items.append([item_url['title'], description, current_price, images, sizes, article, item_url['url']])
                        # это конец, дальше мы сами допишем добавление товаров в БД
                except Exception as ex:
                    logging.warning(f'{cat_name} pr - {ex}')