import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from utils import AddForm

from db import DbDispatcher

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
items = DbDispatcher('items.db')
services = DbDispatcher('services.db')


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
    await AddForm.name.set()
    await message.answer('Введите название товара')


@dp.message_handler(commands=['remove_item'])
async def remove_item(message: types.Message):
    pass


@dp.message_handler(commands=['show_items'])
async def show_items(message: types.Message):
    pass


@dp.message_handler(state=AddForm.name)
async def name(message: types.Message):
    name = message.text
    print(name)
    await AddForm.href_yamarket.set()
    await message.answer(
        'Введите ссылку на товар в яндекс маркете (или None, если отслеживание на этом маркетплейсе не нужно)')


@dp.message_handler(state=AddForm.href_yamarket)
async def ya_href(message: types.Message):
    href_yamarket = message.text
    print(href_yamarket)
    await AddForm.href_ozon.set()
    await message.answer('Введите ссылку на товар на озоне (или None, если отслеживание на этом маркетплейсе не нужно)')


@dp.message_handler(state=AddForm.href_ozon)
async def ozon_href(message: types.Message):
    href_ozon = message.text
    print(href_ozon)
    await AddForm.href_citilink.set()
    await message.answer(
        'Введите ссылку на товар в ситилинке (или None, если отслеживание на этом маркетплейсе не нужно)')


@dp.message_handler(state=AddForm.href_citilink)
async def citilink_href(message: types.Message):
    href_citilink = message.text
    print(href_citilink)
    await message.answer('Товар успешно добавлен в отслеживаемые!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
