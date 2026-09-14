import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import config
from middlewares.auth import AuthMiddleware
from handlers import tasks, callbacks
from scheduler.jobs import daily_habit_check, morning_reminders

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=config.TELEGRAM_TOKEN)
    dp = Dispatcher()

    # Мидлварь на приватность
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Регистрация роутеров
    dp.include_router(callbacks.router)
    dp.include_router(tasks.router) # Tasks всегда последним, так как там ловится любой текст

    # Настройка планировщика (Часовой пояс Минск/Москва UTC+3)
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # 21:00 Чек привычек
    scheduler.add_job(daily_habit_check, CronTrigger(hour=19, minute=47), kwargs={"bot": bot})
    # 08:00 Утренние задачи
    scheduler.add_job(morning_reminders, CronTrigger(hour=8, minute=0), kwargs={"bot": bot})

    scheduler.start()

    print("Bot активирован.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
