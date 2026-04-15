from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from services.user_service import UserService
from services.money_service import MoneyService
from services.cash_account_service import CashAccountService
from handlers.states import NavigationStates
from keyboards.inline import boss_main_keyboard
from keyboards.cash_account_keyboards import (
    get_cash_accounts_keyboard,
    get_cash_account_detail_keyboard,
    get_cancel_change_account_keyboard,
)

router = Router()

@router.callback_query(
    lambda c: c.data == "cash_accounts_list",
)
async def get_all_accounts(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    # Проверяем права
    if not db_user.is_boss:
        await callback.answer("⛔ Только для боссов!", show_alert=True)
        await state.clear()
        return
    await state.set_state(NavigationStates.viewing_accounts_list)
    cash_account_service = CashAccountService(session)
    all_cash_accounts = await cash_account_service.get_all_cash_accounts()
    # Вернем клавиатуру со всеми cash_accounts
    keyboard = get_cash_accounts_keyboard(all_cash_accounts)
    await callback.message.edit_text(
        text=f"Всего счетов: {len(all_cash_accounts)}.",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(
    lambda c: c.data == "exit_from_cash_account_list",
)
async def exit_from_all_accounts(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """Выход из списка аккаунтов на главную страницу"""
    await state.clear()
    keyboard = boss_main_keyboard
    await callback.message.edit_text(
        text=f"Ок, {db_user.username}. Что будем делать?",
        parse_mode="HTML",
        reply_markup=keyboard,
    )

@router.callback_query(lambda c: c.data and c.data.startswith("cash_account_detail_"))
async def get_cash_account_detail(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Обработчик просмотра детальной информации о счете.
    Callback_data format: cash_account_detail_<id>
    Пример: cash_account_detail_2
    """

    # Проверяем права
    if not db_user.is_boss:
        await callback.answer("⛔ Только для боссов!", show_alert=True)
        await state.clear()
        return

    try:
        cash_account_id_str = callback.data.split("_")[-1]
        cash_account_id = int(cash_account_id_str)
    except Exception as e:
        await callback.answer(f"❌ Ошибка {e}", show_alert=True)
        return

    cash_account_service = CashAccountService(session)
    cash_account = await cash_account_service.get_cash_account_by_id(cash_account_id)
    if not cash_account:
        await callback.answer("⛔ Счет не найден.", show_alert=True)
        await state.clear()
        return

    keyboard = get_cash_account_detail_keyboard(cash_account.id)
    text = (f"<b>{cash_account.title}</b>\n"
            f"<i>Баланс</i>: {cash_account.balance} {cash_account.currency}")
    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(lambda c: c.data and c.data.startswith("change_cash_account_title_"))
async def change_cash_account_title(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Изменение названия счета.
    Callback_data format: change_cash_account_title_<id>
    Пример: change_cash_account_title_2
    """

    # Проверяем права
    if not db_user.is_boss:
        await callback.answer("⛔ Только для боссов!", show_alert=True)
        await state.clear()
        return

    try:
        cash_account_id_str = callback.data.split("_")[-1]
        cash_account_id = int(cash_account_id_str)
    except Exception as e:
        await callback.answer(f"❌ Ошибка {e}", show_alert=True)
        return

    await state.set_state(NavigationStates.waiting_change_account_title)
    await state.set_data({
        "cash_account_id": cash_account_id,
        "original_message_id": callback.message.message_id,
    })

    cancel_keyboard = get_cancel_change_account_keyboard(cash_account_id)
    text = "Введите новое название для счета"
    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=cancel_keyboard,
    )


# Изменение баланса счета
@router.callback_query(lambda c: c.data and c.data.startswith("change_cash_account_balance_"))
async def change_cash_account_balance(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Изменение названия счета.
    Callback_data format: change_cash_account_balance_{cash_account_id}
    Пример: change_cash_account_balance_2
    """

    # Проверяем права
    if not db_user.is_boss:
        await callback.answer("⛔ Только для боссов!", show_alert=True)
        await state.clear()
        return

    try:
        cash_account_id_str = callback.data.split("_")[-1]
        cash_account_id = int(cash_account_id_str)
    except Exception as e:
        await callback.answer(f"❌ Ошибка {e}", show_alert=True)
        return

    await state.set_state(NavigationStates.waiting_change_account_balance)
    await state.set_data({
        "cash_account_id": cash_account_id,
        "original_message_id": callback.message.message_id,
    })

    cancel_keyboard = get_cancel_change_account_keyboard(cash_account_id)
    text = "Введите новое значение баланса"
    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=cancel_keyboard,
    )