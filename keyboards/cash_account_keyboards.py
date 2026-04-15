from aiogram.enums import ButtonStyle
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import CashAccount


def get_cash_accounts_keyboard(cash_accounts: list[CashAccount]):
    """Основное меню для employee"""
    builder = InlineKeyboardBuilder()
    for cash_account in cash_accounts:
        builder.button(
            text=f"{cash_account.title}",
            callback_data=f"cash_account_detail_{cash_account.id}",
        )
    builder.button(
        text="Добавить счет 🪙",
        callback_data="add_new_cash_account_btn",
    )
    builder.button(
        text="⬅️ Назад",
        callback_data="exit_from_cash_account_list",
    )
    builder.adjust(1)
    return builder.as_markup()


def get_cash_account_detail_keyboard(cash_account_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Изменить название",
        callback_data=f"change_cash_account_title_{cash_account_id}",
    )
    builder.button(
        text="Изменить баланс",
        callback_data=f"change_cash_account_balance_{cash_account_id}",
    )
    builder.button(
        text="Изменить валюту",
        callback_data=f"change_cash_account_currency_{cash_account_id}",
    )
    builder.button(
        text="УДАЛИТЬ ⚠️",
        callback_data=f"delete_cash_account_{cash_account_id}",
        style=ButtonStyle.DANGER,
    )
    builder.button(text="⬅️ Назад", callback_data="cash_accounts_list")
    builder.adjust(1)
    return builder.as_markup()


def get_cancel_change_account_keyboard(account_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"❌ Отменить",
        callback_data=f"cash_account_detail_{account_id}",
    )
    builder.adjust(1)
    return builder.as_markup()
