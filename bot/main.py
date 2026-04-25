import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import tourist, operator

load_dotenv()


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры — порядок важен!
    dp.include_router(operator.router)  # FSM первым
    dp.include_router(tourist.router)

    print("🏔 NomadJol бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())