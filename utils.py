from aiogram.dispatcher.filters.state import State, StatesGroup


class AddForm(StatesGroup):

    name = State()
    href_yamarket = State()
    href_ozon = State()
    href_citilink = State()

