import hashlib
import json

from bs4 import BeautifulSoup as BS
import requests

headers = {'user-agent':
               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
           'accept': '*/*'
           }

base_url = 'https://prom.ua/Noutbuki'


def main():
    global base_url
    get_data(base_url)


def get_html(url):
    session = requests.Session()
    response = session.get(url, headers=headers)
    if response.ok:
        return response.text


def get_all_pages_url(url):
    html = get_html(url)
    if html:
        try:
            soup = BS(html, features='lxml')
            pagination = soup.find('div', class_='x-pager__content')
            if pagination:
                pages = pagination.findAll('a', class_='x-pager__item')
                page_count = pages.pop(len(pages) - 2).text
                numeric_count = int(page_count)
                if numeric_count > 0:
                    return [url + ';' + str(index) for index in range(1, numeric_count+1)]
        except Exception as e:
            print(e)


def get_data(sub_url):
    urls = get_all_pages_url(sub_url)
    items = {}
    for url in urls:
        try:
            html = get_html(url)
            soup = BS(html, features='lxml')
            item_urls = [tag['href'] for tag in set(soup.findAll('a',class_='x-gallery-tile__tile-link')) if tag.has_attr('href')]
            for item_link in item_urls:
                item_html = get_html(item_link)
                item_soup = BS(item_html, features='lxml')
                media_data = item_soup.find('div', {'data-bazooka': 'ProductGallery'})

                images_url = []
                if media_data:
                    json_data = media_data['data-bazooka-props']
                    for i in json.loads(json_data).get('images'):
                        images_url = [u for u in list(i.values()) if str(u).startswith('https')]

                title_tag = item_soup.find('h1', class_='x-title')
                title = price = ''
                if title_tag:
                    title = title_tag.text.strip()

                price_tag = item_soup.find('div', class_='x-product-price__value')
                if price_tag:
                    price_attr = price_tag['data-qaprice']
                    if price_attr and len(price_attr) > 0:
                        price = str(round(float(price_attr))) + ' грн.'
                    else:
                        continue
                md5 = hashlib.md5()
                md5.update((title + price).encode('utf-8'))
                external_id = md5.hexdigest()

                result_item = {
                    'external_id': external_id,
                    'price': price,
                    'name': title,
                    'media_data': images_url
                }
                items[external_id] = result_item
        except Exception as e:
            print(e)
    with open('test.json', 'w') as out_file:
        out_file.write(json.dumps(list(items.values())))
    return items


if __name__ == '__main__':
    main()
