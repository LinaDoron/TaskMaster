from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class TaskCallback(CallbackData, prefix="t"):
    action: str  # 'done' или 'cancel'
    page_id: str # UUID страницы без дефисов

def get_task_keyboard(page_id: str):
    builder = InlineKeyboardBuilder()
    # Убираем дефисы из ID, чтобы влезть в 64 байта
    short_id = page_id.replace("-", "")
    builder.button(text="✅ Выполнено", callback_data=TaskCallback(action="done", page_id=short_id).pack())
    builder.button(text="❌ Отмена", callback_data=TaskCallback(action="cancel", page_id=short_id).pack())
    return builder.as_markup()
