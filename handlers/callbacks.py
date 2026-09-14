from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline import TaskCallback
from services.notion_api import update_task_status

router = Router()

@router.callback_query(TaskCallback.filter())
async def handle_task_callback(query: CallbackQuery, callback_data: TaskCallback):
    # Восстанавливаем формат UUID с дефисами (Notion схавает и без них, но лучше добавить для надежности, либо Notion API примет 32-char строку. Notion API отлично принимает 32-символьные ID!)
    page_id = callback_data.page_id

    status = "Executed" if callback_data.action == "done" else "Canceled"

    await update_task_status(page_id, status)

    action_text = "выполнена" if status == "Executed" else "отменена"
    await query.message.edit_text(f"{query.message.text}\n\n<i>[Статус обновлен: {action_text}]</i>", parse_mode="HTML")
    await query.answer(f"Задача {action_text}!")
