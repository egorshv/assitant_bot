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
    name = soup.find('h1', class_='_1BWd_ _2OAAC undefined').text
    price = soup.find('div', class_='_3NaXx _3kWlK').find('span').text
    return name, price


def parse_ozon(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        src = f.read()
    soup = BeautifulSoup(src, 'lxml')  # '2\u2009890\u2009'
    name = soup.find('h1', class_='o9j').text
    price = soup.find('span', class_='nj7 n7j').text.replace('\u2009', '')
    return name, price


def parse_citilink(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        src = f.read()
    soup = BeautifulSoup(src, 'lxml')
    name = soup.find('h1', class_='Heading Heading_level_1 ProductHeader__title').text.strip().replace('\\n', '')
    price = soup.find('span',
                      class_='ProductHeader__price-default_current-price js--ProductHeader__price-default_current-price').text.strip().replace(
        '\\n', '')
    return name, price


# TODO: Add DNS parsing function

# get_page('https://www.ozon.ru/product/kvadrokopter-mini-s-kameroy-1080-rx-428009271/?asb=2jJ8vmdVghRw3bMfKFQAVyHH5ttt0X1H9vh0MYrNaWuW%252FB4Zg%252BQk4PtWDTiwtg%252Bg&asb2=Ns1psh_iy1DRWm_lCoXzkl3JUe7bHR5GY0eWHIx1mK2nCEaJZ4LhzK2xNxrxm8MbOCx2PjJVgUnEAEfvGnnwc_XCTFT-nRbZo-5NBrWrDxKfxuOmGG8Me2c5v2fONFZyD_xwMw3fZx-KRa0PeyhLFQ&sh=grPT_44urQ',
#          'page.html')
# print(parse_ozon('page.html'))
