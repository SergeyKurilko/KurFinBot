from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.database import get_session

class SessionMiddleware(BaseMiddleware):
    """
    Middleware для инъекции сессии БД.
    Сессия живет ровно время обработки одного запроса. "unot-of-work"
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Создаем сессию для этого запроса
        async with get_session() as session:
            # Инжектим сессию в данные
            data["session"] = session
            # Передаем управление хэндлеру
            result = await handler(event, data)

            # После выполнения хэндлера сессия автоматически закроется
            return result
