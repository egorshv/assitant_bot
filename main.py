import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from utils import AddForm, RemoveForm
from pars import get_page, parse_ozon, parse_citilink, parse_yamarket
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db import DbDispatcher

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
items = DbDispatcher('items.db')
services = DbDispatcher('services.db')
prices = DbDispatcher('prices.db')
YAMARKET = True
OZON = True
inline_kb1 = InlineKeyboardMarkup()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет! Это бот для отслеживания цены на различные товары.\n'
                         'Для просмотра команд введи /help')


@dp.message_handler(commands=['help'])
async def help_(message: types.Message):
    await message.answer('Команды бота:\n'
                         '/set_markets - ? настроить маркетплейсы, где отслеживается цена\n'
                         '/add_item - добавить отслеживаемый товар\n'
                         '/remove_item - удалить товар из отслеживаемых\n'
                         '/show_items - просмотр всех отслеживаемых товаров\n'
                         '/show_details - ?\n')


@dp.message_handler(commands=['set_markets'])
async def set_markets(message: types.Message):
    pass


@dp.message_handler(commands=['add_item'])
async def add_item(message: types.Message):
    await AddForm.href_yamarket.set()
    await message.answer(
        'Введите ссылку на товар в яндекс маркете (или None, если отслеживание на этом маркетплейсе не нужно)')


@dp.message_handler(commands=['remove_item'])
async def remove_item(message: types.Message):
    await RemoveForm.id.set()
    await message.answer('Введите id товара, который надо удалить\n/show_items - для просмотра товаров')


@dp.message_handler(state=RemoveForm.id)
async def removing_by_id(message: types.Message):
    try:
        _id = int(message.text)
        await message.answer('Все работает')
    except ValueError:
        await RemoveForm.id.set()
        await message.answer('Некорректный id, попробуйте ещё раз')


@dp.message_handler(commands=['show_items'])
async def show_items(message: types.Message):
    itms = items.select_data({}, 'items', columns=['name'])
    s = ''
    for i in range(len(itms)):
        s += f'{itms[i][0]} ({i + 1})\n'
        btn = InlineKeyboardButton(itms[i][0], callback_data=f'btn_{i}')
        inline_kb1.add(btn)
    await message.answer(s, reply_markup=inline_kb1)


# @dp.callback_query_handler(func=lambda c: c.data == 'btn_0')
# async def callback_data_btn0(callback_query: types.CallbackQuery):
#     pass


@dp.message_handler(state=AddForm.href_yamarket)
async def ya_href(message: types.Message):
    global YAMARKET
    href_yamarket = message.text
    corr_url = True
    try:
        get_page(href_yamarket, 'yamarket.html')
    except Exception:
        corr_url = False
    if href_yamarket.lower() != 'none' and not corr_url:
        name, price = parse_yamarket('yamarket.html')
        price = int(price[:-2])
        items.write_data({'name': name}, 'items')
        item_id = items.get_max_id('items')[0]
        services.write_data({'item_id': item_id, 'href': href_yamarket}, 'services')
        serv_id = services.get_max_id('services')[0]
        curr_price = prices.select_data({'item_id': item_id, 'serv_id': serv_id}, 'prices', ['price'])
        try:
            if curr_price != price:
                prices.write_data(
                    {'item_id': item_id, 'serv_id': serv_id, 'date': datetime.today().strftime('%Y-%m-%d'),
                     'price': price},
                    'prices')
        except TypeError:
            prices.write_data(
                {'item_id': item_id, 'serv_id': serv_id, 'date': datetime.today().strftime('%Y-%m-%d'), 'price': price},
                'prices')
    else:
        YAMARKET = False
    await AddForm.href_ozon.set()
    await message.answer('Введите ссылку на товар на озоне (или None, если отслеживание на этом маркетплейсе не нужно)')


@dp.message_handler(state=AddForm.href_ozon)
async def ozon_href(message: types.Message):
    global OZON, YAMARKET
    href_ozon = message.text
    if href_ozon.lower() != 'none':
        get_page(href_ozon, 'ozon.html')
        name, price = parse_ozon('ozon.html')
        price = int(price[:-2])
        if not YAMARKET:
            items.write_data({'name': name}, 'items')
        item_id = items.get_max_id('items')[0]
        services.write_data({'item_id': item_id, 'href': href_ozon}, 'services')
        serv_id = services.get_max_id('services')[0]
        curr_price = prices.select_data({'item_id': item_id, 'serv_id': serv_id}, 'prices', ['price'])
        try:
            if curr_price != price:
                prices.write_data(
                    {'item_id': item_id, 'serv_id': serv_id, 'date': datetime.today().strftime('%Y-%m-%d'),
                     'price': price},
                    'prices')
        except TypeError:
            prices.write_data(
                {'item_id': item_id, 'serv_id': serv_id, 'date': datetime.today().strftime('%Y-%m-%d'), 'price': price},
                'prices')
    else:
        OZON = False
    await AddForm.href_citilink.set()
    await message.answer(
        'Введите ссылку на товар в ситилинке (или None, если отслеживание на этом маркетплейсе не нужно)')


@dp.message_handler(state=AddForm.href_citilink)
async def citilink_href(message: types.Message, state: FSMContext):
    global YAMARKET, OZON
    href_citilink = message.text
    if href_citilink.lower() != 'none':
        get_page(href_citilink, 'citilink.html')
        name, price = parse_citilink('citilink.html')
        if not YAMARKET and not OZON:
            items.write_data({'name': name}, 'items')
        item_id = items.get_max_id('items')[0]
        services.write_data({'item_id': item_id, 'href': href_citilink}, 'services')
        serv_id = services.get_max_id('services')[0]
        curr_price = prices.select_data({'item_id': item_id, 'serv_id': serv_id}, 'prices', ['price'])
        try:
            if curr_price != price:
                prices.write_data(
                    {'item_id': item_id, 'serv_id': serv_id, 'date': datetime.today().strftime('%Y-%m-%d'),
                     'price': price},
                    'prices')
        except TypeError:
            prices.write_data(
                {'item_id': item_id, 'serv_id': serv_id, 'date': datetime.today().strftime('%Y-%m-%d'), 'price': price},
                'prices')
    await message.answer('Товар успешно добавлен в отслеживаемые!')
    await state.finish()


async def shutdown(dispatcher: Dispatcher):
    items.close_connection()
    services.close_connection()
    prices.close_connection()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
