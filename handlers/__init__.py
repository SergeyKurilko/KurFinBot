from aiogram import Dispatcher
from aiogram.filters import CommandStart, Command

from handlers.commands import start, admin
from handlers.boss_callbacks import router as boss_callbacks_router
from handlers.boss_handlers import router as boss_handlers_router
from handlers.employee_callbacks import router as employee_callbacks_router


def setup_handlers(dp: Dispatcher):
    """
    Регистрация всех хэндлеров
    """
    # Регистрируем роутеры команд
    dp.include_router(start.router)

    dp.include_router(boss_callbacks_router)
    dp.include_router(boss_handlers_router)
    dp.include_router(employee_callbacks_router)

