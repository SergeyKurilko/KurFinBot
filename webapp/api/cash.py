# webapp/api/cash.py
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio.session import AsyncSession

from webapp.api.auth import verify_telegram_init_data
from webapp.dependencies import get_db_session
from webapp.models import UpdateAccountRequest
from services.user_service import UserService
from services.cash_account_service import CashAccountService

router = APIRouter()


@router.get("/cash-accounts")
async def get_cash_accounts(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db_session=Depends(get_db_session),
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

        if user.is_boss:
            cash_account_service = CashAccountService(db_session)
            cash_accounts = await cash_account_service.get_all_cash_accounts()
            accounts = []
            for cash_account in cash_accounts:
                accounts.append(
                    {
                        "id": cash_account.id,
                        "title": cash_account.title,
                        "balance": cash_account.balance,
                        "currency": cash_account.currency,
                    }
                )
            return {"status": "ok", "accounts": accounts}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cash-accounts/{account_id}")
async def get_cash_account_by_id(
    account_id: int,
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db_session=Depends(get_db_session),
):
    """
    Получить информацию о конкретном счете по ID
    """
    try:
        # Проверяем подпись
        telegram_user = verify_telegram_init_data(init_data)
        user_service = UserService(db_session)
        # Получаем пользователя из БД
        user = await user_service.get_user(telegram_user["id"])

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Проверяем, что пользователь имеет доступ (только для босса)
        if not user.is_boss:
            raise HTTPException(
                status_code=403, detail="Access denied. Only for bosses"
            )

        cash_account_service = CashAccountService(db_session)
        cash_account = await cash_account_service.get_cash_account_by_id(account_id)

        if not cash_account:
            raise HTTPException(status_code=404, detail="Cash account not found")

        balance_in_rubles = getattr(cash_account, "balance_in_rubles", None)

        # Формируем ответ
        account_data = {
            "id": cash_account.id,
            "title": cash_account.title,
            "balance": cash_account.balance,
            "currency": cash_account.currency,
            "balance_in_rubles": balance_in_rubles,
        }
        return {"status": "ok", "account": account_data}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/cash-accounts/{account_id}")
async def update_cash_account(
    account_id: int,
    request: UpdateAccountRequest,
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    Обновить данные кассового счета
    """
    try:
        # Проверяем подпись Telegram
        telegram_user = verify_telegram_init_data(init_data)

        # Получаем пользователя из БД
        user_service = UserService(db_session)
        user = await user_service.get_user(telegram_user["id"])

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Проверяем, что пользователь имеет доступ (только для босса)
        if not user.is_boss:
            raise HTTPException(
                status_code=403, detail="Access denied. Only for bosses"
            )

        # Получаем счет
        cash_account_service = CashAccountService(db_session)

        # Проверяем, что хотя бы одно поле для обновления передано
        if (
            request.balance is None
            and request.title is None
            and request.currency is None
        ):
            raise HTTPException(
                status_code=400, detail="At least one field must be provided for update"
            )

        # Обновляем поля
        updated_account = None

        if request.balance is not None:
            updated_account = await cash_account_service.update_account_balance(
                account_id, int(request.balance)
            )
        elif request.title is not None:
            updated_account = await cash_account_service.update_account_title(
                account_id, request.title
            )
        elif request.currency is not None:
            updated_account = await cash_account_service.update_account_currency(
                account_id, request.currency
            )

        if not updated_account:
            raise HTTPException(status_code=404, detail="Cash account not found")

        # Возвращаем обновленные данные
        return {
            "status": "ok",
            "message": "Account updated successfully",
            "account": {
                "id": updated_account.id,
                "title": updated_account.title,
                "balance": updated_account.balance,
                "currency": updated_account.currency,
                "balance_in_rubles": getattr(
                    updated_account, "balance_in_rubles", None
                ),
            },
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cash-accounts/{account_id}")
async def delete_cash_account(
    account_id: int,
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    Удаление счета
    """
    try:
        # Проверяем подпись Telegram
        telegram_user = verify_telegram_init_data(init_data)

        # Получаем пользователя из БД
        user_service = UserService(db_session)
        user = await user_service.get_user(telegram_user["id"])

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Проверяем, что пользователь имеет доступ (только для босса)
        if not user.is_boss:
            raise HTTPException(
                status_code=403, detail="Access denied. Only for bosses"
            )

        # Получаем счет
        cash_account_service = CashAccountService(db_session)
        account = await cash_account_service.get_cash_account_by_id(account_id)

        if not account:
            raise HTTPException(status_code=404, detail="Cash account not found")

        await cash_account_service.delete_cash_account(account_id)

        # Возвращаем обновленные данные
        return {
            "status": "ok",
            "message": "Account is deleted",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cash-accounts")
async def create_cash_account(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    Создание нового счета
    """
    try:
        # Проверяем подпись Telegram
        telegram_user = verify_telegram_init_data(init_data)

        # Получаем пользователя из БД
        user_service = UserService(db_session)
        user = await user_service.get_user(telegram_user["id"])

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Проверяем, что пользователь имеет доступ (только для босса)
        if not user.is_boss:
            raise HTTPException(
                status_code=403, detail="Access denied. Only for bosses"
            )

        # Получаем счет
        cash_account_service = CashAccountService(db_session)
        new_account = await cash_account_service.create_new_account(
            title="Новый счет",
            balance=0,
            currency="RUB",
        )
        if new_account:
            return {
                "status": "ok",
                "message": "New account created",
                "cash_account_id": new_account.id,
            },
        else:
            raise ValueError("Cash account creation failed")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(status_code=500, detail=str(e))