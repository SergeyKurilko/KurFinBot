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

    # profile_menu = State()        # Меню профиля
    # scores_menu = State()         # Меню score
    # admin_menu = State()          # Меню администратора
    # settings_menu = State()       # Меню настроек