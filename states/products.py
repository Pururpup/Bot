from aiogram.fsm.state import StatesGroup, State

class ProductStates(StatesGroup):
    wait_find_prod = State()
    wait_add_name = State()
    wait_add_receipt_date = State()
    wait_add_purchase_price = State()
    wait_add_sale_date = State()
    wait_add_sale_price = State()
    wait_add_repair_price = State()
    wait_add_quantity_in_stock = State()
    wait_add_quantity_in_delivery = State()
    wait_choose_category = State()
    wait_choose_loc_of_purchase = State()
    wait_choose_loc_of_sale = State()
    wait_save_product = State()
    wait_del_prod = State()