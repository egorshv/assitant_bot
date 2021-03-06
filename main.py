import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from utils import AddForm, RemoveForm
from pars import get_page, parse_ozon, parse_citilink, parse_yamarket
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile

from db import DbDispatcher
from get_plt import create_plot

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
items = DbDispatcher('items.db')
services = DbDispatcher('services.db')
prices = DbDispatcher('prices.db')
YAMARKET = True
OZON = True


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


# @dp.message_handler(commands=['set_markets'])
# async def set_markets(message: types.Message):
#     pass


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
async def removing_by_id(message: types.Message, state: FSMContext):
    try:
        _id = int(message.text)
        items.delete_data({'id': _id}, 'items')
        services.delete_data({'item_id': _id}, 'services')
        prices.delete_data({'item_id': _id, }, 'prices')
        await message.answer('Товар успешно удалён')
        await state.finish()
    except ValueError:
        await RemoveForm.id.set()
        await message.answer('Некорректный id, попробуйте ещё раз')


@dp.message_handler(commands=['show_items'])
async def show_items(message: types.Message):
    itms = items.select_data({}, 'items', columns=['name'])
    inline_kb1 = InlineKeyboardMarkup()
    s = ''
    for i in range(len(itms)):
        s += f'{itms[i][0]} ({i + 1})\n\n'
        btn = InlineKeyboardButton(itms[i][0], callback_data=f'btn_{i + 1}')
        inline_kb1.add(btn)
    await message.answer(s, reply_markup=inline_kb1)


@dp.callback_query_handler(lambda c: 'btn' in c.data)
async def callback_data_btn(callback_query: types.CallbackQuery):
    id = int(callback_query.data[-1])
    arr = prices.select_data({'item_id': id}, 'prices')
    title = items.select_data({'id': id}, 'items', columns=['name'])[0][0]
    file_name = f'item{id}.png'
    pr = []
    dates = []
    for item in arr:
        pr.append(item[0])
        dates.append(item[1])
    await bot.answer_callback_query(callback_query.id)
    if len(dates) > 2:
        create_plot(dates, pr, file_name, title)
        file = InputFile(file_name)
        await bot.send_photo(callback_query.from_user.id, file)
    else:
        await bot.send_message(callback_query.from_user.id, 'Не хватает данных для построения графика')


@dp.message_handler(state=AddForm.href_yamarket)
async def ya_href(message: types.Message):
    global YAMARKET  # Флаг для записи в бд
    href_yamarket = message.text
    corr_url = True  # Проверка валидности ссылки
    try:
        get_page(href_yamarket, 'yamarket.html')
    except Exception as e:
        corr_url = False
    if href_yamarket.lower() == 'none':
        YAMARKET = False
        await AddForm.href_ozon.set()
        await message.answer(
            'Введите ссылку на товар на озоне (или None, если отслеживание на этом маркетплейсе не нужно)')
    elif not corr_url:
        await AddForm.href_yamarket.set()
        await message.answer('Некорректная ссылка, попробуйте снова')
    else:
        try:  # try нужен, чтобы проверить, удается ли спарсить страницу
            name, price = parse_yamarket('yamarket.html')
            price = int(price[:-2])
            items.write_data({'name': name}, 'items')
            item_id = items.get_max_id('items')[0]
            services.write_data({'item_id': item_id, 'href': href_yamarket}, 'services')
            serv_id = services.get_max_id('services')[0]
            curr_price = prices.select_data({'item_id': item_id, 'serv_id': serv_id}, 'prices', ['price'])
            if int(curr_price) != price:  # Если текущая цена равна предыдущей, то нет смысла записывать
                prices.write_data(
                    {'item_id': item_id, 'serv_id': serv_id, 'date': datetime.today().strftime('%Y-%m-%d'),
                     'price': price},
                    'prices')

        except Exception as e:
            YAMARKET = False
            await message.answer('Сейчас не получается получить доступ к этой странице')

        await AddForm.href_ozon.set()
        await message.answer(
            'Введите ссылку на товар на озоне (или None, если отслеживание на этом маркетплейсе не нужно)')


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
    corr_url = True
    try:
        get_page(href_citilink, 'citilink.html')
    except Exception as e:
        corr_url = False
    if href_citilink.lower() == 'none':
        await message.answer('Товар успешно добавлен в отслеживаемые!')
        await state.finish()
    elif not corr_url:
        await AddForm.href_citilink.set()
        await message.answer('Некорректная ссылка, попробуйте снова')
    else:
        try:
            name, price = parse_citilink('citilink.html')
            if not YAMARKET and not OZON:
                items.write_data({'name': name}, 'items')
            item_id = items.get_max_id('items')[0]
            services.write_data({'item_id': item_id, 'href': href_citilink}, 'services')
            serv_id = services.get_max_id('services')[0]
            curr_price = prices.select_data({'item_id': item_id, 'serv_id': serv_id}, 'prices', ['price'])
            if int(curr_price) != price:
                prices.write_data(
                    {'item_id': item_id, 'serv_id': serv_id, 'date': datetime.today().strftime('%Y-%m-%d'),
                     'price': price},
                    'prices')
        except Exception as e:
            await message.answer('Сейчас не получается получить доступ к этой странице')
        await message.answer('Товар успешно добавлен в отслеживаемые!')
        await state.finish()


@dp.message_handler()
async def wrong_message(message: types.Message):
    await message.answer('Команда не распознана.\nДля просмотра команд используйте /help')


async def shutdown(dispatcher: Dispatcher):
    items.close_connection()
    services.close_connection()
    prices.close_connection()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
