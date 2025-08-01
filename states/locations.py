from aiogram.fsm.state import StatesGroup, State


class LocationStates(StatesGroup):
    wait_add_name = State()
    wait_add_address = State()
    wait_del = State()