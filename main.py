import logging
from aiogram import Bot, Dispatcher
from config import config
from handlers import products, categories, locations, photos, other

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(products.router, categories.router, locations.router, photos.router, other.router)

if __name__ == '__main__':
    dp.run_polling(bot)

