from aiogram import Router, F
from aiogram.types import Message
from services.deepseek_api import parse_user_intent
from services.notion_api import create_task, get_all_pending_tasks, update_task_status, create_today_habit_page, update_habit_checkboxes, get_today_habit
from config import config

router = Router()

@router.message(F.text)
async def handle_new_task(message: Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        pending_tasks = await get_all_pending_tasks()

        intent_data = await parse_user_intent(message.text, pending_tasks)
        action = intent_data.get("action")

# 3. Маршрутизация действий
        if action == "create":
            task = intent_data.get("task", "Неизвестная задача")
            date = intent_data.get("date")
            severity = intent_data.get("severity", "Medium")
            await create_task(task, date, severity)
            await message.reply(f"✅ Задача сохранена.\nСуть: {task}\nДата: {date}\nВажность: {severity}")

        elif action == "close":
            page_id = intent_data.get("page_id")
            if page_id:
                await update_task_status(page_id, "Executed")
                await message.reply("Принято. Твоя эффективность на приемлемом уровне. Задача закрыта.")
            else:
                await message.reply("Я не нашел активную задачу с таким описанием в твоей Памяти. Проверь базу.")

        elif action == "create_habit_page":
            page_id, is_new = await create_today_habit_page()
            if is_new:
                await message.reply(f"🤖 Отчет на сегодня успешно создан, {config.USER_NAME}.")
            else:
                await message.reply(f"🤖 Отчет на сегодня уже создан, {config.USER_NAME}.")
        elif action == "update_habit":
            habits = intent_data.get("habits", [])
            page_id, _ = await create_today_habit_page()

            if habits:
                try:
                    await update_habit_checkboxes(page_id, habits)
                    habits_str = ", ".join(habits)
                    await message.reply(f"Зафиксировано: <b>{habits_str}</b>.\n<i>Приемлемо, пока что ты меня не разочаровываешь.</i>", parse_mode="HTML")
                except Exception as e:
                    print(f"NOTION ERROR CHECKBOXES: {e}")
                    await message.reply("Ошибка. Не удалось поставить галочки в Notion.")
            else:
                await message.reply("Я не понял, какую именно привычку нужно отметить.")

        else:
            await message.reply(f"❌ Команда не распознана, {config.USER_NAME}. Сформулируйте запрос иначе.")

    except Exception as e:
        import traceback
        full_error = traceback.format_exc()
        print(f"DEBUG ERROR FULL: {full_error}") # Печатаем в консоль ВСЁ
        # В телегу шлем чуть больше информации
        await message.reply(f"Ошибка: {type(e).__name__}")
