from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from config import config
from services.notion_api import get_today_habit, update_habit_verdict, get_today_tasks, update_task_log
from services.deepseek_api import analyze_habits, generate_morning_reminder
from keyboards.inline import get_task_keyboard

async def daily_habit_check(bot: Bot):
    habit = await get_today_habit()
    if not habit:
        await bot.send_message(config.ADMIN_ID, "Вы не создали отчет за сегодня.")
        return

    verdict = await analyze_habits(habit["rate"], habit["note"])
    await update_habit_verdict(habit["page_id"], verdict)

    try:
        await bot.send_message(config.ADMIN_ID, f"Оценка дня:\n\n{verdict}", parse_mode="HTML")
    except TelegramBadRequest:
        # Если ИИ накосячил с тегами, отправляем без HTML
        await bot.send_message(config.ADMIN_ID, f"Оценка дня:\n\n{verdict}", parse_mode=None)

async def morning_reminders(bot: Bot):
    tasks = await get_today_tasks()
    if not tasks:
        await bot.send_message(config.ADMIN_ID, "На сегодня задач в Памяти нет. Можешь расслабиться.")
        return

    for task in tasks:
        reminder = await generate_morning_reminder(task["title"], task["severity"])
        await update_task_log(task["page_id"], reminder)

        kb = get_task_keyboard(task["page_id"])

        try:
            await bot.send_message(
                config.ADMIN_ID,
                f"<b>{task['severity']} TASK</b>\n\n{reminder}",
                reply_markup=kb,
                parse_mode="HTML"
            )
        except TelegramBadRequest:
            # Страховка от кривых тегов ИИ
            await bot.send_message(
                config.ADMIN_ID,
                f"{task['severity']} TASK\n\n{reminder}",
                reply_markup=kb,
                parse_mode=None
            )
