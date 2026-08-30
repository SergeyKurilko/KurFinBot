#!/usr/bin/env python3
"""
Главный файл запуска бота
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage  # для продакшена
from aiogram.client.session.aiohttp import AiohttpSession # для проксирования

from bot.config import config
from database.database import init_db, dispose_engine
from bot.middlewares.session_middleware import SessionMiddleware
from bot.middlewares.user_middleware import UserMiddleware
from handlers import setup_handlers
from bot.scheduler import start_scheduler, stop_scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if config.environment == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, dispatcher: Dispatcher):
    """
    Действия при запуске бота
    Выполняются ДО начала поллинга
    """
    logger.info("Бот запускается...")

    # Инициализация базы данных
    await init_db()
    logger.info("База данных инициализирована")

    # Запуск планировщика
    await start_scheduler()

    # Здесь можно добавить другие действия при запуске:
    # - Очистка временных данных
    # - Проверка подключений
    # - Загрузка конфигураций
    # - Установка вебхука (если используете webhook вместо polling)

    # Уведомление администраторов о запуске
    # for admin_id in config.admin_ids:
    #     try:
    #         await bot.send_message(admin_id, "✅ Бот запущен!")
    #     except Exception as e:
    #         logger.error(f"Не удалось уведомить админа {admin_id}: {e}")
    #
    # logger.info("🎉 Бот успешно запущен!")


async def on_shutdown(bot: Bot, dispatcher: Dispatcher):
    """
    Действия при остановке бота
    Выполняются ПОСЛЕ остановки поллинга
    """
    logger.info("Бот останавливается...")

    # Остановка планировщика
    await stop_scheduler()

    # Уведомление администраторов
    # for admin_id in config.admin_ids:
    #     try:
    #         await bot.send_message(admin_id, "🛑 Бот останавливается...")
    #     except Exception:
    #         pass

    # Закрытие соединений с БД
    await dispose_engine()
    logger.info("Соединения с БД закрыты")

    # Закрытие сессии бота
    await bot.session.close()
    logger.info("Сессия бота закрыта")
    logger.info("Бот остановлен")


async def main():
    """Главная функция запуска"""

    # 1. Создаем бота
    # proxy_url = config.proxy
    # bot_session = AiohttpSession(proxy=proxy_url)
    # bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode='HTML'), session=bot_session)
    bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode='HTML'))

    # 2. Выбираем хранилище для FSM (Finite State Machine)
    if config.environment == "production":
        # В продакшене используем Redis для хранения состояний
        from redis import Redis

        redis = Redis(host="localhost", port=6379, decode_responses=True)
        storage = RedisStorage(redis=redis)
        logger.info("📦 Используется Redis storage")
    else:
        # В разработке - память
        storage = MemoryStorage()
        logger.info("Используется Memory storage")

    # 3. Создаем диспетчер
    dp = Dispatcher(storage=storage)

    # 4. Регистрируем middleware (порядок важен!)
    dp.update.middleware(SessionMiddleware())
    dp.update.middleware(UserMiddleware())
    logger.info("Middleware зарегистрированы")

    # 5. Регистрируем хэндлеры
    setup_handlers(dp)
    logger.info("Хэндлеры зарегистрированы")

    # 6. Регистрируем функции запуска/остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # 7. Запускаем бота
    try:
        logger.info(f"Бот {bot.id} запущен в режиме {config.environment}")

        # Выбор метода получения обновлений
        if config.environment == "production" and os.getenv("USE_WEBHOOK"):
            # Для продакшена с вебхуком
            webhook_url = os.getenv("WEBHOOK_URL")
            await bot.set_webhook(webhook_url)
            logger.info(f"Вебхук установлен: {webhook_url}")

            # Запуск через вебхук (нужен веб-сервер)
            # await dp.start_webhook(...)
        else:
            # Поллинг (для разработки и небольших ботов)
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types(),
                skip_updates=True,  # Пропустить старые обновления
            )
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise
    finally:
        # Дополнительная очистка при экстренной остановке
        await storage.close()
        logger.info("Ресурсы очищены")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Необработанная ошибка: {e}", exc_info=True)
        sys.exit(1)
