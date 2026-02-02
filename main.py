import asyncio
import logging
import time
import gc
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.start import register_start_handlers
from handlers.supercell import register_supercell_handlers
from handlers.telegram import register_telegram_handlers
from handlers.admin_panel import register_admin_handler

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем хендлеры
    register_start_handlers(dp)
    register_supercell_handlers(dp)
    register_telegram_handlers(dp)

    register_admin_handler(dp)

    await bot.delete_webhook()
    # Запускаем поллинг
    while True:
        try:
            await dp.start_polling(bot)
        except:
            time.sleep(2)
            gc.collect()

if __name__ == "__main__":
    asyncio.run(main())

