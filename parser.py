from bs4 import BeautifulSoup
import requests


def get_page(url, filename):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(r.text)


def parse_yamarket(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        src = f.read()
    soup = BeautifulSoup(src, 'lxml')
    price = soup.find('div', class_='_3NaXx _3kWlK').find('span').text
    return price


def parse_ozon(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        src = f.read()
    soup = BeautifulSoup(src, 'lxml')
    price = soup.find('span', class_='c2h5 c2h6').text
    return price

# get_page('https://www.ozon.ru/product/smartfon-xiaomi-redmi-note-10s-6-128gb-belyy-288651911/?sh=KUaJg78h', 'page.html')
# print(parse_ozon('page.html'))
