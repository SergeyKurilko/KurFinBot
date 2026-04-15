from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError
import logging

from services.scheduler_service import DailyRewardScheduler

logger = logging.getLogger(__name__)

# Глобальный экземпляр планировщика
scheduler = AsyncIOScheduler()


def setup_scheduler():
    """Настройка планировщика задач"""

    # Очищаем существующие задачи (если есть)
    try:
        scheduler.remove_job("daily_reward_morning")
    except JobLookupError:
        pass

    try:
        scheduler.remove_job("daily_reward_evening")
    except JobLookupError:
        pass

    # Проверка начислений на утро
    scheduler.add_job(
        DailyRewardScheduler.run_daily_rewards_job,
        trigger=CronTrigger(hour=6, minute=0),
        id="daily_reward_morning",
        name="Ежедневное начисление наград (утро)",
        replace_existing=True,
    )

    # Проверка начислений на вечер
    scheduler.add_job(
        DailyRewardScheduler.run_daily_rewards_job,
        trigger=CronTrigger(hour=19, minute=0),
        id="daily_reward_evening",
        name="Ежедневное начисление наград (вечер)",
        replace_existing=True,
    )

    logger.info("⏰ Планировщик настроен: задачи на 6:00 и 19:00")

    # # Опционально: добавить задачу для тестирования (каждые 1 минуту)
    # scheduler.add_job(
    #     DailyRewardScheduler.run_daily_rewards_job,
    #     trigger=CronTrigger(minute='*/1'),
    #     id='daily_reward_test',
    #     name='Тестовое начисление (каждые 5 минут)',
    #     replace_existing=True
    # )


async def start_scheduler():
    """Запуск планировщика"""
    setup_scheduler()
    scheduler.start()
    logger.info("✅ Планировщик задач запущен")


async def stop_scheduler():
    """Остановка планировщика"""
    scheduler.shutdown(wait=True)
    logger.info("🛑 Планировщик задач остановлен")
