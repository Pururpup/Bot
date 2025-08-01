from aiogram.fsm.state import StatesGroup, State

class CategoryStates(StatesGroup):
    wait_add = State()
    wait_del = State()
