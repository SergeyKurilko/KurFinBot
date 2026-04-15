from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from keyboards.inline import boss_main_keyboard, get_employees_main_keyboard
from handlers.states import NavigationStates

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: types.Message,
    session: AsyncSession,
    state: FSMContext,
    db_user: User = None,
):
    """
    Обработчик команды /start
    """
    # Очищаем состояние (если было)
    await state.clear()
    if db_user:
        # Приветственное сообщение
        welcome_text = (
            f"👋 Привет, {db_user.username}!\n\n"
        )
        mew_state = NavigationStates.boss_main_menu if db_user.is_boss else NavigationStates.employee_main_menu
        await state.set_state(mew_state)
        keyboard = boss_main_keyboard if db_user.is_boss else get_employees_main_keyboard(employee_id=db_user.id)
        # Отправляем сообщение
        await message.delete()
        await message.answer(welcome_text, reply_markup=keyboard)
    else:
        # Пользователя нет в БД
        return
