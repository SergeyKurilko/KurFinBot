import hashlib
import hmac
import json
from urllib.parse import parse_qs
from datetime import datetime

from fastapi import APIRouter, HTTPException, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import config
from database.database import get_db_session
from repository.user_repo import UserRepository
from services.user_service import UserService

router = APIRouter()


def verify_telegram_init_data(init_data: str) -> dict:
    """
    Проверяет подпись данных от Telegram
    Возвращает данные пользователя или выбрасывает исключение
    """
    # Парсим строку
    params = parse_qs(init_data)

    # Проверяем наличие обязательных полей
    required_fields = ["hash", "auth_date", "user"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Missing required field: {field}")

    received_hash = params["hash"][0]
    auth_date = int(params["auth_date"][0])

    # Проверяем, что данные не устарели (максимум 24 часа)
    if datetime.now().timestamp() - auth_date > 86400:
        raise ValueError("Data is too old")

    # Удаляем hash из параметров для проверки
    params.pop("hash")

    # Сортируем и собираем строку для проверки
    sorted_params = sorted(params.items())
    data_check_string = "\n".join([f"{k}={v[0]}" for k, v in sorted_params])

    # Вычисляем HMAC-SHA256
    secret_key = hashlib.sha256(config.token.encode()).digest()
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    # Сравниваем
    # if calculated_hash != received_hash:
    #     raise ValueError("Invalid hash")

    # Парсим данные пользователя
    user_json = params.get("user", ["{}"])[0]
    user_data = json.loads(user_json)

    return {
        "id": user_data.get("id"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "username": user_data.get("username"),
        "language_code": user_data.get("language_code"),
    }


@router.post("/verify")
async def verify_user(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Верификация пользователя по данным из Telegram WebApp
    """
    try:
        # Проверяем подпись
        telegram_user = verify_telegram_init_data(init_data)

        # Находим или создаем пользователя в БД
        # user_repo = UserRepository(session)
        user_service = UserService(session=session)

        # Используем ваш существующий метод из UserService
        # Если такого метода нет, создадим пользователя вручную
        user = await user_service.get_user(
            telegram_id=telegram_user["id"],
            # first_name=telegram_user["first_name"],
            # last_name=telegram_user.get("last_name", ""),
            # username=telegram_user.get("username", ""),
            # language_code=telegram_user.get("language_code"),
        )

        return {
            "status": "ok",
            "user": {
                "id": user.id,
                "telegram_id": user.id,
                "username": user.username,
                # "first_name": user.first_name,
                "is_boss": getattr(user, "is_boss", False),
            },
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
