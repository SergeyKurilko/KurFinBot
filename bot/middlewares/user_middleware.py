from aiogram import BaseMiddleware
from services.user_service import UserService


class UserMiddleware(BaseMiddleware):
    """
    Middleware для проверки пользователя.
    Использует сессию из SessionMiddleware.
    """

    async def __call__(self, handler, event, data):
        # Сессия уже есть в data (из SessionMiddleware)
        session = data.get("session")
        if not session:
            return await handler(event, data)

        # Получаем Telegram User
        telegram_user = self._get_telegram_user(event)
        if not telegram_user:
            return await handler(event, data)

        # Используем сервис с той же сессией
        user_service = UserService(session)
        db_user = await user_service.get_user(telegram_id=telegram_user.id)
        if not db_user:
            print(f"Пришел левый чувак!{'*' * 55}")
            return await handler(event, data)

        # Инжектим в хэндлер
        data["db_user"] = db_user
        data["user_service"] = user_service

        return await handler(event, data)

    def _get_telegram_user(self, event):
        """Извлекаем Telegram User из разных типов событий"""
        if hasattr(event, "from_user"):
            return event.from_user
        if hasattr(event, "message") and event.message:
            return event.message.from_user
        if hasattr(event, "callback_query") and event.callback_query:
            return event.callback_query.from_user
        return None
