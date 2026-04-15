from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from services.user_service import UserService
from services.money_service import MoneyService
from handlers.states import NavigationStates
from keyboards.inline import (
    get_employee_my_profile_keyboard,
    get_employees_main_keyboard
)

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("my_employee_profile_"))
async def get_my_employee_profile(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Обработчик просмотра своего профиля для сотрудника.
    """

    # Получаем данные сотрудника
    employee = await user_service.get_user(db_user.id)

    if not employee:
        await callback.answer("❌ Профиль не найден", show_alert=True)
        return

    # Получаем финансовую информацию сотрудника
    money_service = MoneyService(session)
    money_info = await money_service.get_money_info_by_user_id(db_user.id)
    await state.set_state(NavigationStates.boss_employee_detail)
    # Формируем информацию о состоянии Money сотрудника
    profile_text = (
        f"👤 <b>Профиль</b>\n\n"
        f"Имя: {employee.username or 'Не указано'}\n"
        f"⭐️ Score: {money_info.scores}\n"
        f"💰 Баланс: {money_info.balance} руб.\n\n"
        f"Ежедневный бонус: {money_info.daily_reward} руб."
    )

    # Клавиатура с действиями для этого сотрудника
    keyboard = get_employee_my_profile_keyboard()
    await callback.message.edit_text(
        profile_text, parse_mode="HTML", reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data and c.data.startswith("employee_main_menu"))
async def employee_main_menu(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Переход на главное меню из коллбэков.
    """
    # Получаем данные сотрудника
    keyboard = get_employees_main_keyboard(db_user.id)
    await callback.message.edit_text(
        "Ок. Что будем делать?", parse_mode="HTML", reply_markup=keyboard
    )