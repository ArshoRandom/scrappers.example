from bs4 import BeautifulSoup
import requests
import xlsxwriter

headers = {
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,hy;q=0.6',
           'cookie': 'cf_clearance=e5da2cb4068d0979769af6222d26675ace743cda-1589278535-0-150; __cfduid=d5e31cbefed2b73167d2a9e338519ad441589278535; PHPSESSID=ks9kkjd6maojeev1dllf6re74f; _csrf=iL-dvevgA6jPDN_JZHBaILCgqqAppRDd; goon=0; _ga=GA1.2.1439938296.1589278536; _gid=GA1.2.537167495.1589278536; _ym_uid=1589278537290054822; _ym_d=1589278537; _ym_isad=2; d2mid=33gzA9FZRGhWwejn3O0vxHyxmnuWBQ; _ym_visorc_53889418=w; chat-position-left=1543px; chat-opened=0; chat-position-top=429px',
           'sec-fetch-mode': 'navigate',
           'sec-fetch-site': 'none',
           'sec-fetch-user': '?1',
           'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
}
base_url = 'https://market.dota2.net/'



def get_content(url, headers):
    session = requests.Session()
    session.trust_env = False
    response = session.get(url, headers=headers)
    if response.ok:
        return response.text


def main():
    data = get_data(get_pages(base_url))
    write_excel(data)


def get_pages(url):
    html = get_content(url, headers)
    soup = BeautifulSoup(html, features='html.parser')
    pages_count_tag = soup.find('span', {'id': 'total_pages'})
    if pages_count_tag:
        pages_count = int(pages_count_tag.text.strip())
        pages_url = [f'https://market.dota2.net/?r=&q=&p={i}' for i in range(1,pages_count+1)]
        return pages_url


def get_data(urls_list):
    data = []
    if len(urls_list) > 0:
        for url in urls_list:
            try:
                html = get_content(url, headers)
                soup = BeautifulSoup(html,features='html.parser')
                items_container = soup.find('div', {'class': 'market-items', 'id': 'applications'})
                if items_container:
                    all_items = items_container.select('a[href^="/item/"]')
                    if len(all_items) > 0:
                        name = price = ''
                        for item in all_items:
                            name_tag = item.find('div', class_='name')
                            price_tag = item.find('div', class_='price')
                            if name_tag: name = name_tag.text.strip()
                            if price_tag: price = price_tag.text.strip()
                            if len(name) > 0 and len(price) > 0:
                                data.append((name, price))
            except Exception as e:
                print(e)
        return data


def write_excel(data_list):
    workbook = xlsxwriter.Workbook('data.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0,0,'Name')
    worksheet.write(0,1,'Price')
    row = 1
    for index in range(len(data_list)):
        worksheet.write(row,0,data_list[index][0])
        worksheet.write(row,1,data_list[index][1])
        row += 1
    workbook.close()

if __name__ == '__main__':
    main()
