import hashlib
import json
import re
import traceback
from datetime import datetime

import requests
from bs4 import BeautifulSoup, NavigableString

def main():
    raw_store_data = get_store_data()
    if not raw_store_data or len(raw_store_data) == 0:
        raise ValueError('Something was changed in retailer side.')


def _get_opening_hours(raw_data):
    if raw_data and len(raw_data) > 0:
        open_hours = ''
        chunks = []
        if ',' in raw_data:
            chunks = raw_data.split(',')
        elif '/' in raw_data:
            chunks = raw_data.split('/')
        elif re.match(r'.*\d{2}[:]\d{2}.* Uhr .*\d{2}[:]\d{2}.*', raw_data):
            chunks = raw_data.split('Uhr')
        else:
            chunks.append(raw_data)
        for chunk in chunks:
            if len(chunk) > 0:
                chunk = chunk.strip()
                if '-' in chunk or 'ab' in chunk:
                    chunk = chunk.replace('.', ' ').replace('/', '').replace(',', '')
                    if re.match(r'.*ab\s+\d{1,2}[:]\d{2}', chunk):
                        if '-' not in chunk:
                            chunk = chunk.replace('ab ', '').replace('Uhr', '') + '-24:00'
                        else:
                            chunk = chunk.split('-')[0].replace('ab ', '') + '-24:00'
                    if 'Uhr' in chunk:
                        chunk = chunk.replace('Uhr', '')
                    if re.match('.*\d{1,2}\s\d{2}', chunk):
                        wrong_part = re.findall(r'\d{1,2}\s\d{2}', chunk)[0]
                        valid_part = wrong_part.replace(' ', ':')
                        chunk = chunk.replace(wrong_part, valid_part)
                    if re.match('.*\d{1,2}[:]\d{2}[:]\d*.', chunk):
                        tokens = chunk.split('-')
                        for token in tokens:
                            parts = token.split(':')
                            if len(parts) == 3:
                                valid_token = parts[0] + ':' + parts[1]
                                wr_part = re.findall(r'.*\d{1,2}[:]\d{2}[:]\d{2}', chunk)[0]
                                chunk = chunk.replace(wr_part, valid_token)
                else:
                    tokens = chunk.split(':')
                    if len(tokens) == 4:
                        chunk = tokens[0] + ':' + tokens[1] + '-' + tokens[2] + ':' + tokens[3]
                        chunk.strip()
                open_hours += chunk + ';'
                open_hours = open_hours.replace('´', '')

        return open_hours


def get_store_data():
    stores = {}
    now = datetime.utcnow()
    url = 'https://www.ihle.de/alle-standorte.html'
    try:
        response = requests.get(url)
        if response.ok:
            bs = BeautifulSoup(response.text, features='lxml')
            locations = bs.findAll('div', {'class': 'panel panel-default'})
            for location in locations:

                try:
                    city = ''
                    heading = location.find('div', {'class': 'panel-heading'})
                    if heading:
                        city = heading.text.strip()
                    data_containers = location.findAll('p')
                    for data in data_containers:
                        address = telephone = opening_hours = zip_code = external_id = ''
                        name = data.findChild('strong').text.strip()
                        items = data.contents
                        offline = False
                        for item in items:
                            if isinstance(item, NavigableString) and 'telefon' in item.lower():
                                telephone = item.split(':')[1].strip()
                            elif isinstance(item, NavigableString) and re.match(r'.*\d{5}\s*.', item):
                                zip_code = re.findall(r'\d{5}', item)[0]
                                address = item.split(',')[0].strip()
                                if address or zip_code or city:
                                    md5 = hashlib.md5()
                                    md5.update((zip_code + address).encode('utf-8'))
                                    external_id = md5.hexdigest()
                            elif isinstance(item, NavigableString) \
                                    and re.match(r'Mo|Fr|Sa|So', item) \
                                    and 'geschlossen' not in item:
                                opening_hours = _get_opening_hours(item)

                                # if market closing date less than now
                            elif isinstance(item, NavigableString) \
                                    and re.match(r'.*\d{1,2}[.]\d{1,2}[.]\d{4}.*geschlossen*.', item) \
                                    and datetime.strptime(re.findall(r'\d{2}\.\d{2}\.\d{4}', item)[0].split('T')[0],
                                                          '%d.%m.%Y') < now:
                                opening_hours = ''
                            elif isinstance(item, NavigableString) \
                                    and re.match(r'zur\s+zeit\s+geschlossen', item.strip().lower()):
                                offline = True
                                opening_hours = ''

                            # If opening hours is exists but market start working from date where greate now
                            elif isinstance(item, NavigableString) \
                                    and re.match(r'.*er.ffnung.*\d{1,2}[.]\d{1,2}[.]\d{4}', item.strip().lower()) \
                                    and len(opening_hours.strip()) > 0 \
                                    and datetime.strptime(re.findall(r'\d{2}\.\d{2}\.\d{4}', item)[0].split('T')[0],
                                                          '%d.%m.%Y') > now:
                                opening_hours = ''

                        store = {
                            'external_id': external_id,
                            'name': name,
                            'city': city,
                            'address': address,
                            'zip_code': zip_code,
                            'telephone': telephone,
                            'opening_hours': opening_hours,
                            'latitude': 0.0,
                            'longitude': 0.0,
                            'offline': offline
                        }
                        stores[external_id] = store
                except:
                    print('Unexpected error:', traceback.format_exc())
    except:
        print('Unexpected error:', traceback.format_exc())
    with open('test.json', 'w') as out_file:
        out_file.write(json.dumps(list(stores.values())))
    return stores.values()

if __name__ == '__main__':
    main()