from aiogram.dispatcher.filters.state import State, StatesGroup


class AddForm(StatesGroup):
    href_yamarket = State()
    href_ozon = State()
    href_citilink = State()


class RemoveForm(StatesGroup):
    name = State()
