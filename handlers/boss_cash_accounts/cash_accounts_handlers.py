from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from keyboards.cash_account_keyboards import (
    get_cancel_change_account_keyboard,
    get_cash_account_detail_keyboard,
)
from services.cash_account_service import CashAccountService
from handlers.states import NavigationStates
from keyboards.inline import (
    boss_main_keyboard,
)

router = Router()

@router.message(StateFilter(NavigationStates.waiting_change_account_title))
async def process_cash_account_title_input(
    message: types.Message,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
):
    """
    Обработка ввода нового значения title для CashAccount
    """
    # Проверяем права
    if not db_user.is_boss:
        await message.answer("⛔ Только для боссов!")
        await state.clear()
        return

    # Получаем сохраненные данные
    data = await state.get_data()
    cash_account_id = data.get("cash_account_id")
    original_message_id = data.get("original_message_id")

    # Парсим введенное значение
    new_title = message.text.strip()

    # Проверяем, что длина нормальная
    if len(new_title) <= 3 or len(new_title) > 50:
        cancel_keyboard = get_cancel_change_account_keyboard(cash_account_id)
        await message.answer(
            "❌ Длина названия счета должна быть от 3 до 30",
            reply_markup=cancel_keyboard,
        )
        await message.delete()
        return

    # Обновляем cash_account_service через сервис
    cash_account_service = CashAccountService(session)

    try:
        updated_cash_account = await cash_account_service.update_account_title(account_id=cash_account_id, new_title=new_title)

        if not updated_cash_account:
            await message.answer("❌ Ошибка: запись не найдена")
            await state.clear()
            return

        # Успешное обновление
        keyboard = get_cash_account_detail_keyboard(cash_account_id)
        text = (
            f"<b>{updated_cash_account.title}</b>\n"
            f"<i>Баланс</i>: {updated_cash_account.balance} {updated_cash_account.currency}"
        )

        # Отвечаем на сообщение
        await message.answer(
            text,
            reply_markup=keyboard,
        )

        # Пробуем обновить оригинальное сообщение с callback
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=original_message_id,
                reply_markup=None,
            )
        except Exception:
            pass  # Игнорируем ошибку, если сообщение уже не существует

        # Очищаем состояние
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении: {e}")
        await state.clear()


@router.message(StateFilter(NavigationStates.waiting_change_account_balance))
async def process_cash_account_balance_input(
    message: types.Message,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
):
    """
    Обработка ввода нового значения balance для CashAccount
    """
    # Проверяем права
    if not db_user.is_boss:
        await message.answer("⛔ Только для боссов!")
        await state.clear()
        return

    # Получаем сохраненные данные
    data = await state.get_data()
    cash_account_id = data.get("cash_account_id")
    original_message_id = data.get("original_message_id")

    # Парсим введенное значение
    try:
        new_balance = int(message.text.strip())
        # Проверяем, что значение положительное
        if new_balance <= 0:
            cancel_keyboard = get_cancel_change_account_keyboard(cash_account_id)
            await message.answer(
                "❌ Баланс должен быть положительным числом!\n"
                "Попробуйте еще раз или нажмите 'Отмена':",
                reply_markup=cancel_keyboard(cash_account_id),
            )
            await message.delete()
            return
    except Exception:
        cancel_keyboard = get_cancel_change_account_keyboard(cash_account_id)
        await message.answer(
            "❌ Баланс должен быть положительным числом без пробелов! Например: 100 или 50000 \n"
            "Попробуйте еще раз или нажмите 'Отмена':",
            reply_markup=cancel_keyboard,
        )
        await message.delete()
        return


    # Обновляем cash_account_service через сервис
    cash_account_service = CashAccountService(session)

    try:
        updated_cash_account = await cash_account_service.update_account_balance(account_id=cash_account_id, new_balance=new_balance)

        if not updated_cash_account:
            await message.answer("❌ Ошибка: запись не найдена")
            await state.clear()
            return

        # Успешное обновление
        keyboard = get_cash_account_detail_keyboard(cash_account_id)
        text = (
            f"<b>{updated_cash_account.title}</b>\n"
            f"<i>Баланс</i>: {updated_cash_account.balance} {updated_cash_account.currency}"
        )

        # Отвечаем на сообщение
        await message.answer(
            text,
            reply_markup=keyboard,
        )

        # Пробуем обновить оригинальное сообщение с callback
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=original_message_id,
                reply_markup=None,
            )
        except Exception:
            pass  # Игнорируем ошибку, если сообщение уже не существует

        # Очищаем состояние
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении: {e}")
        await state.clear()