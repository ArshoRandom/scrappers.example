from bs4 import BeautifulSoup
import requests

base_url = 'https://buff.163.com/api/market/goods?game=dota2&page_num=1&_=1589288777474'


def main():
    get_data(get_pages(base_url))


def get_pages(url):
    response = requests.get(url)
    if response.ok:
        data = response.json()
        pages_count = data.get('data').get('total_page')
        urls = [f'https://buff.163.com/api/market/goods?game=dota2&page_num={i}&_=1589288777474' for i in range(1,pages_count+1)]
        print(urls)





def get_data(urls_list):
    pass



if __name__ == '__main__':
    main()