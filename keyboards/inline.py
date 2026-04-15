from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import User

boss_main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Получатели", callback_data="employees_list")],
        [InlineKeyboardButton(text="Сбережения 🪙", callback_data="cash_accounts_list")],
    ]
)

def get_employees_main_keyboard(employee_id):
    """Основное меню для employee"""
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Мой профиль", callback_data=f"my_employee_profile_{employee_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_employee_my_profile_keyboard():
    """Меню при просмотре своего профиля для employee"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=f"employee_main_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_employees_list_keyboard(employees_list: List[User]):
    """Список получателей"""
    builder = InlineKeyboardBuilder()
    for employee in employees_list:
        builder.button(
            text=f"{employee.username}", callback_data=f"employee_profile_{employee.id}"
        )
    builder.button(text="⬅️ Назад", callback_data="boss_main_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_employee_actions_keyboard(employee_id, money_id):
    """Действия с получателем"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💸 Выплатить бонус 💸", callback_data=f"pay_out_menu_{employee_id}_{money_id}"
    )
    builder.button(text="➕ Добавить очки", callback_data=f"add_score_{employee_id}_{money_id}")
    builder.button(text="➖ Списать очки", callback_data=f"remove_score_{employee_id}_{money_id}")
    builder.button(
        text="⚙️ Изменить бонус", callback_data=f"change_daily_reward_{employee_id}_{money_id}"
    )
    builder.button(text="⬅️ Назад", callback_data=f"employees_list")
    builder.adjust(1)
    return builder.as_markup()


def add_score_keyboard(money_id, employee_id):
    """Выбор количества очков для добавления"""
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ 1 ⭐", callback_data=f"confirm_add_score_1_{money_id}")
    builder.button(text="➕ 2 ⭐", callback_data=f"confirm_add_score_2_{money_id}")
    builder.button(text="➕ 3 ⭐", callback_data=f"confirm_add_score_3_{money_id}")
    builder.button(text="⬅️ Назад", callback_data=f"employee_profile_{employee_id}")
    builder.adjust(1)
    return builder.as_markup()

def reduce_score_keyboard(money_id, employee_id):
    """Выбор количества очков для убавления"""
    builder = InlineKeyboardBuilder()
    builder.button(text="➖ 1 ⭐", callback_data=f"confirm_red_score_1_{money_id}")
    builder.button(text="➖ 2 ⭐", callback_data=f"confirm_red_score_2_{money_id}")
    builder.button(text="➖ 3 ⭐", callback_data=f"confirm_red_score_3_{money_id}")
    builder.button(text="⬅️ Назад", callback_data=f"employee_profile_{employee_id}")
    builder.adjust(1)
    return builder.as_markup()

def change_daily_reward_keyboard(employee_id):
    """Клавиатура во время ожидания введения нового daily_reward"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=f"employee_profile_{employee_id}")
    builder.adjust(1)
    return builder.as_markup()

def pay_out_waiting_keyboard(employee_id):
    """Клавиатура во время ожидания подтверждения списания"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтверждаю выплату ✅️", callback_data="confirm_pay_out_waiting")
    builder.button(text="⬅️ Назад", callback_data=f"employee_profile_{employee_id}")
    builder.adjust(1)
    return builder.as_markup()