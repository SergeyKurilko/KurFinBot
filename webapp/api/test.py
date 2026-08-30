# webapp/api/test.py
from fastapi import APIRouter, Depends, HTTPException, Header

from webapp.api.auth import verify_telegram_init_data
from webapp.dependencies import get_user_service, get_db_session
from services.user_service import UserService

router = APIRouter()


@router.get("/me")
async def get_current_user(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db_session = Depends(get_db_session),
):
    """
    Получить информацию о текущем пользователе
    """
    try:
        # Проверяем подпись
        telegram_user = verify_telegram_init_data(init_data)
        user_service = UserService(db_session)
        # Получаем пользователя из БД
        user = await user_service.get_user(telegram_user["id"])

        if not user:
            return {"status": "error", "message": "User not found"}

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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ping")
async def ping():
    """Простой тестовый эндпоинт без авторизации"""
    return {"status": "ok", "message": "pong"}
