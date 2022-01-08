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
    name = soup.find('h1', class_='e8j2').text
    price = soup.find('span', class_='c2h5 c2h6').text.replace('\u2009', '')
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


# get_page('https://market.yandex.ru/product--15-6-noutbuk-asus-tuf-gaming-f15-fx506hcb-hn1138t-1920x1080-intel-core-i5-2-7-ggts-ram-8-gb-ssd-512-gb-geforce-rtx-3050-win10-home/1416870731?cpc=DZym8dOiCoQKWVCipYbfhrm2Log3ya88-nicGmy8-mpsNJ1n_HaAa9WchQFPZyRDovXxdg-ObzBM9R_mUrT8kn9xSuI9yaF2VG_M6t6Qj-pJaetzpiL9-4zTVWkNQ72iMt92oajtcx-7W9w0WtYrcdBX2Ens5z5Sm6FR3SX9y59b0fAMHDdgJ4p49VM444Cz&sku=101419888781&offerid=UFU5N2L98IP0KzPYywJFNA&cpa=1',
#          'page.html')
# print(parse_yamarket('page.html'))
