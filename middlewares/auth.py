from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from config import config

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        # Если пишет чужой
        if user_id != config.ADMIN_ID:
            if isinstance(event, Message):
                await event.answer("⛔ Доступ запрещен. Вы не являетесь администратором этого бота.")
            elif isinstance(event, CallbackQuery):
                await event.answer("Доступ запрещен.", show_alert=True)
            return

        # Если это ты - пропускаем
        return await handler(event, data)
