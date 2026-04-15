from aiogram.fsm.state import State, StatesGroup

class NavigationStates(StatesGroup):
    """Состояния навигации по меню"""
    boss_main_menu = State()           # Главное меню босса
    employee_main_menu = State()       # Главное меню сотрудника

    employees_list = State()              # Меню-Список всех получателей
    boss_employee_detail = State()        # Меню профиля получателя для босса
    waiting_score_number_add = State()    # Ожидание количества добавляемых score
    waiting_score_number_remove = State() # Ожидание количества убавляемых score
    change_daily_reward = State()         # Меню изменения размера вознаграждения
    waiting_pay_out_confirm = State()     # Ожидание подтверждения выплаты

    # Cash accounts navigations
    viewing_accounts_list = State()           # Просмотр списка счетов
    waiting_change_account_title = State()    # Ожидание нового названия счета
    waiting_change_account_balance = State()  # Ожидание нового баланса для счета
    waiting_change_account_currency = State() # Ожидание нового currency для счета
    waiting_confirm_delete_account = State()  # Ожидание подтверждения удаления счета

    # profile_menu = State()        # Меню профиля
    # scores_menu = State()         # Меню score
    # admin_menu = State()          # Меню администратора
    # settings_menu = State()       # Меню настроек