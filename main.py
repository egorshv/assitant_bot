import logging

from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


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
    pass


@dp.message_handler(commands=['remove_item'])
async def remove_item(message: types.Message):
    pass


@dp.message_handler(commands=['show_items'])
async def show_items(message: types.Message):
    pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
