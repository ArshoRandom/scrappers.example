import json
import traceback
import requests

def main():
    raw_store_data = get_store_data()
    if not raw_store_data or len(raw_store_data) == 0:
        raise ValueError('Something was changed in retailer side.')


def get_store_data():
    stores = {}
    week_days = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so']
    try:
        response = requests.get('https://www.ankerbrot.at/io/?&io=get_filialen')
        if response.ok:
            data = response.json()
            for raw_store in data:
                try:
                    if raw_store.get('country') == 'AT':
                        external_id = raw_store.get('id')
                        zip_code = raw_store.get('postal_code')
                        address = raw_store.get('street') + ' ' + raw_store.get('street_nr')
                        longitude = raw_store.get('lng')
                        latitude = raw_store.get('lat')
                        city = raw_store.get('city')
                        telephone = raw_store.get('telephone').replace(' ', '')
                        name = raw_store.get('custom_address')
                        if name is None or len(name) == 0:
                            name = address
                        opening_hours = ''
                        for day in week_days:
                            time = raw_store.get(day)
                            if len(time) > 0:
                                opening_hours += day + ' ' + time + ';'
                        if '00:00' in opening_hours:
                            opening_hours = opening_hours.replace('00:00', '24:00')
                        if not latitude or not longitude:
                            latitude, longitude = 0.0, 0.0

                        store_data = {
                            'external_id': external_id,
                            'name': name,
                            'opening_hours': opening_hours,
                            'city': city,
                            'zip_code': zip_code,
                            'address': address,
                            'longitude': float(longitude),
                            'latitude': float(latitude),
                            'telephone': telephone,
                        }
                        stores[external_id] = store_data
                except:
                    print("Unexpected error:", traceback.format_exc())
    except:
        print("Unexpected error:", traceback.format_exc())
    with open('api_scrapper/test.json', 'w') as out_file:
        out_file.write(json.dumps(list(stores.values())))
    return stores.values()

if __name__ == '__main__':
    main()