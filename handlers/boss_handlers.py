from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from services.user_service import UserService
from services.money_service import MoneyService
from handlers.states import NavigationStates
from keyboards.inline import (
    get_employees_list_keyboard,
    boss_main_keyboard,
    get_employee_actions_keyboard,
    add_score_keyboard,
    reduce_score_keyboard,
    change_daily_reward_keyboard
)

router = Router()

@router.message(StateFilter(NavigationStates.change_daily_reward))
async def process_daily_reward_input(
    message: types.Message,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
):
    """
    Обработка ввода нового значения daily reward
    """
    # Проверяем права
    if not db_user.is_boss:
        await message.answer("⛔ Только для боссов!")
        await state.clear()
        return

    # Получаем сохраненные данные
    data = await state.get_data()
    employee_id = data.get("employee_id")
    money_id = data.get("money_id")
    original_message_id = data.get("original_message_id")

    # Парсим введенное значение
    try:
        new_reward = int(message.text.strip())

        # Проверяем, что значение положительное
        if new_reward <= 0:
            await message.answer(
                "❌ Ежедневный бонус должен быть положительным числом!\n"
                "Попробуйте еще раз или нажмите 'Отмена':",
                reply_markup=change_daily_reward_keyboard(employee_id),
            )
            return

        # Ограничиваем максимальное значение (опционально)
        if new_reward > 1000:
            await message.answer(
                "⚠️ Слишком большое значение! Максимальный бонус - 1000 р.\n"
                "Попробуйте еще раз:",
                reply_markup=change_daily_reward_keyboard(employee_id),
            )
            return

    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите целое число!\n"
            "Пример: 5, 10, 100\n\n"
            "Попробуйте еще раз:",
            reply_markup=change_daily_reward_keyboard(employee_id),
        )
        return

    # Обновляем daily_reward через сервис
    money_service = MoneyService(session)

    try:
        updated_money = await money_service.update_daily_reward(money_id, new_reward)

        if not updated_money:
            await message.answer("❌ Ошибка: запись не найдена")
            await state.clear()
            return

        # Успешное обновление
        success_text = (
            f"✅ <b>Ежедневный бонус успешно изменен!</b>\n\n"
            f"Новое значение: <code>{new_reward}</code> руб.\n\n"
            f"<i>Теперь все новые начисления и списания будут использовать этот бонус.</i>"
        )

        # Отвечаем на сообщение
        await message.answer(success_text, parse_mode="HTML")

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

        # Показываем главное меню
        await message.answer(
            "Ок. Что будем делать?",
            reply_markup=boss_main_keyboard,
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении: {e}")
        await state.clear()
