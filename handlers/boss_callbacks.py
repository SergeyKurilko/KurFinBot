from aiogram import Router, types
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
    change_daily_reward_keyboard,
    pay_out_waiting_keyboard,
    pay_out_partial_keyboard,
)

router = Router()


@router.callback_query(lambda c: c.data == "boss_main_menu")
async def go_to_main_menu(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    await state.set_state(NavigationStates.boss_main_menu)
    await callback.message.edit_text(
        text="Ок. Что будем делать?", reply_markup=boss_main_keyboard, parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data == "employees_list")
async def get_employees_list_profile_menu(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Список всех получателей.
    """
    # Проверяем текущее состояние
    current_state = await state.get_state()

    # if current_state != NavigationStates.boss_main_menu.state:
    #     await callback.answer("❌ Недоступно из текущего меню", show_alert=True)
    #     return
    employees = await user_service.get_all_employees()
    employees_list_keyboard = get_employees_list_keyboard(employees)
    # Обновляем состояние
    await state.set_state(NavigationStates.employees_list)

    # Отвечаем на callback и обновляем сообщение
    # await callback.answer("Выберите получателя")
    await callback.message.edit_text(
        text="Выберите получателя",
        reply_markup=employees_list_keyboard,
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data and c.data.startswith("employee_profile_"))
async def get_employee_profile(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Обработчик просмотра профиля сотрудника.
    Callback_data format: employee_profile_<employee_id>
    Пример: employee_profile_1575703477
    """
    # Извлекаем ID сотрудника из callback_data
    employee_id_str = callback.data.split("_")[-1]

    try:
        employee_id = int(employee_id_str)
    except ValueError:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return

    # Проверяем права: только босс может смотреть профили сотрудников
    if not db_user.is_boss:
        await callback.answer(
            "⛔ Только боссы могут просматривать профили сотрудников!", show_alert=True
        )
        return

    # Получаем данные сотрудника
    employee = await user_service.get_user(employee_id)

    if not employee:
        await callback.answer("❌ Профиль не найден", show_alert=True)
        return

    # Получаем финансовую информацию сотрудника
    money_service = MoneyService(session)
    money_info = await money_service.get_money_info_by_user_id(employee_id)
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
    keyboard = get_employee_actions_keyboard(employee.id, money_info.id)
    await callback.message.edit_text(
        profile_text, parse_mode="HTML", reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data and c.data.startswith("add_score_"))
async def select_add_score(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Меню ручного добавления score для получателя.
    Callback_data format: add_score_<employee_id>_<money_id>
    Пример: add_score_1575703477
    """
    # Извлекаем ID сотрудника и ID Money из callback_data
    try:
        employee_id_str = callback.data.split("_")[-2]
        money_id_str = callback.data.split("_")[-1]
        employee_id = int(employee_id_str)
        money_id = int(money_id_str)
    except ValueError:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return
    await state.set_state(NavigationStates.waiting_score_number_add)
    keyboard = add_score_keyboard(money_id=money_id, employee_id=employee_id)
    text = "Добавить очки"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith("confirm_add_score_"))
async def confirm_add_score(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Подтверждение добавления очков в money
    Callback_data format: confirm_add_score_<scores>_<money_id>
    Пример: add_score_1575703477
    """
    # Извлекаем ID сотрудника и ID Money из callback_data
    try:
        money_id_str = callback.data.split("_")[-1]
        scores_str = callback.data.split("_")[-2]
        money_id = int(money_id_str)
        scores = int(scores_str)
    except ValueError:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return
    money_service = MoneyService(session)
    try:
        updated_money = await money_service.add_score_by_money_id(
            money_id=money_id, scores=scores
        )
    except Exception as e:
        await callback.answer(
            f"Что-то пошло не так при начислении score в money: {money_id}. ERROR: {e}",
            show_alert=True,
        )
        return
    new_balance = updated_money.balance
    new_score = updated_money.scores
    await callback.answer(
        f"Добавлено score: {scores}. \n\n"
        f"⭐️ Score: {new_score}\n"
        f"💰 Баланс: {new_balance} руб.",
        show_alert=True,
    )
    await state.set_state(NavigationStates.boss_main_menu)
    keyboard = boss_main_keyboard
    text = "Ок. Что будем делать?"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith("remove_score_"))
async def select_reduce_score(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Меню ручного убавления score для получателя.
    Callback_data format: remove_score_<employee_id>_<money_id>
    Пример: remove_score_1575703477_2
    """
    # Извлекаем ID сотрудника и ID Money из callback_data
    try:
        employee_id_str = callback.data.split("_")[-2]
        money_id_str = callback.data.split("_")[-1]
        employee_id = int(employee_id_str)
        money_id = int(money_id_str)
    except ValueError:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return
    await state.set_state(NavigationStates.waiting_score_number_remove)
    keyboard = reduce_score_keyboard(money_id=money_id, employee_id=employee_id)
    text = "Списать очки"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith("confirm_red_score_"))
async def confirm_reduce_score(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Подтверждение убавления очков в money
    Callback_data format: confirm_red_score_<scores>_<money_id>
    Пример: confirm_red_score_1575703477_2
    """
    # Извлекаем ID сотрудника и ID Money из callback_data
    try:
        money_id_str = callback.data.split("_")[-1]
        scores_str = callback.data.split("_")[-2]
        money_id = int(money_id_str)
        scores = int(scores_str)
    except ValueError:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return
    money_service = MoneyService(session)
    try:
        updated_money = await money_service.reduce_score_by_money_id(
            money_id=money_id, scores=scores
        )
    except Exception as e:
        await callback.answer(
            f"Что-то пошло не так при списании score в money: {money_id}. ERROR: {e}",
            show_alert=True,
        )
        return
    new_balance = updated_money.balance
    new_score = updated_money.scores
    await callback.answer(
        f"Списано score: {scores}. \n\n"
        f"⭐️ Score: {new_score}\n"
        f"💰 Баланс: {new_balance} руб.",
        show_alert=True,
    )
    keyboard = boss_main_keyboard
    await state.set_state(NavigationStates.boss_main_menu)
    text = "Ок. Что будем делать?"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith("change_daily_reward_"))
async def change_daily_reward(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Изменение ежедневного бонуса (вознаграждения) для money.
    Callback_data format: change_daily_reward_<employee_id>_<money_id>
    Пример: change_daily_reward_1575703477_2
    """
    # Извлекаем ID сотрудника и ID Money из callback_data
    try:
        employee_id_str = callback.data.split("_")[-2]
        money_id_str = callback.data.split("_")[-1]
        employee_id = int(employee_id_str)
        money_id = int(money_id_str)
    except ValueError:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return
    await state.set_state(NavigationStates.change_daily_reward)
    await state.update_data(
        employee_id=employee_id,
        money_id=money_id,
        original_message_id=callback.message.message_id,
    )
    keyboard = change_daily_reward_keyboard(employee_id=employee_id)
    text = (
        "Введи новое значение для ежедневного бонуса. "
        "Новый размер бонуса будет применен ко всем новым начислениям и списаниям!"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith("pay_out_menu_"))
async def pay_out_money_menu(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Выплата для money. Получение состояния подтверждения списания и проверка доступности списания.
    Callback_data format: pay_out_menu_{employee_id}_{money_id}
    Пример: pay_out_menu_123456789_2
    """
    # Извлекаем ID сотрудника и ID Money из callback_data
    try:
        employee_id_str = callback.data.split("_")[-2]
        money_id_str = callback.data.split("_")[-1]
        employee_id = int(employee_id_str)
        money_id = int(money_id_str)
    except ValueError:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return
    money_service = MoneyService(session)
    money = await money_service.get_money_info_by_user_id(employee_id)
    if money.balance <= 0:
        await callback.answer(
            f"❌ Выплата недоступна при нулевом или отрицательном балансе.\nТекущий баланс: {money.balance} руб.",
            show_alert=True,
        )
        return
    await state.set_state(NavigationStates.waiting_pay_out_confirm)
    await state.update_data(
        employee_id=employee_id,
        money_id=money_id,
        original_message_id=callback.message.message_id,
    )
    keyboard = pay_out_waiting_keyboard(employee_id=employee_id)
    text = (
        "⚠️ <b>Внимание!</b> Нажимая <code>Подтверждаю выплату</code>, "
        "<b>баланс</b> и <b>score</b> будут сброшены на <i>0</i>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(
    lambda c: c.data == "confirm_pay_out_waiting",
    NavigationStates.waiting_pay_out_confirm,
)
async def confirm_pay_out(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Подтверждение выплаты.
    Срабатывает только когда:
    1. callback_data = "confirm_pay_out_waiting"
    2. Пользователь находится в состоянии NavigationStates.waiting_pay_out_confirm
    """
    # Проверяем права
    if not db_user.is_boss:
        await callback.answer("⛔ Только для боссов!", show_alert=True)
        await state.clear()
        return

    # Получаем данные из состояния
    data = await state.get_data()
    employee_id = data.get("employee_id")
    money_id = data.get("money_id")
    original_message_id = data.get("original_message_id")

    if not employee_id or not money_id:
        await callback.answer("❌ Ошибка: данные не найдены", show_alert=True)
        await state.clear()
        return

    # Выполняем выплату
    money_service = MoneyService(session)

    try:
        # Получаем текущий баланс для отчета
        money = await money_service.get_money_info_by_user_id(employee_id)

        if not money or money.balance <= 0:
            await callback.answer(
                f"❌ Выплата недоступна при нулевом или отрицательном балансе.\n"
                f"Текущий баланс: {money.balance if money else 0} руб.",
                show_alert=True,
            )
            await state.clear()
            return

        paid_balance = money.balance
        paid_scores = money.scores

        # Выполняем выплату через репозиторий
        updated_money = await money_service.pay_out(money_id)

        # Успешная выплата
        success_text = (
            f"✅ Выплата успешно выполнена!\n\n"
            f"💰 Выплачено: {paid_balance} руб.\n"
            f"⭐️ Списано score: {paid_scores}\n\n"
        )

        await callback.answer(text=success_text, show_alert=True)

        # Очищаем состояние
        await state.clear()

        # Обновляем сообщение
        await callback.message.edit_text(
            text="Ок. Что будем делать?",
            parse_mode="HTML",
            reply_markup=boss_main_keyboard,
        )



        # Опционально: уведомить сотрудника о выплате
        # try:
        #     await callback.bot.send_message(
        #         employee_id,
        #         f"✅ Вам произведена выплата!\n"
        #         f"💰 Сумма: {paid_balance} руб.\n"
        #         f"⭐️ Списано score: {paid_scores}",
        #     )
        # except Exception:
        #     pass  # Не удалось отправить уведомление

    except Exception as e:
        await callback.answer(f"❌ Ошибка при выплате: {e}", show_alert=True)
        await state.clear()


@router.callback_query(lambda c: c.data and c.data.startswith("pay_out_partial_menu_"))
async def pay_out_partial(
    callback: types.CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
    user_service: UserService,
):
    """
    Меню ручного убавления score для получателя.
    Callback_data format: remove_score_<employee_id>_<money_id>
    Пример: remove_score_1575703477_2
    """
    # Извлекаем ID сотрудника и ID Money из callback_data
    try:
        employee_id_str = callback.data.split("_")[-2]
        money_id_str = callback.data.split("_")[-1]
        employee_id = int(employee_id_str)
        money_id = int(money_id_str)
    except ValueError:
        await callback.answer("❌ Неверный формат данных", show_alert=True)
        return
    await state.set_state(NavigationStates.waiting_pay_out_partial_input)
    await state.update_data(
        employee_id=employee_id,
        money_id=money_id,
        original_message_id=callback.message.message_id,
    )
    keyboard = pay_out_partial_keyboard(employee_id=employee_id)
    text = "Введите сумму для выплаты"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)