from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Money
from database.database import async_session_factory
import logging

logger = logging.getLogger(__name__)


class RewardService:
    """Сервис для управления ежедневными наградами"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def process_daily_rewards(self) -> dict:
        """
        Проверяет всех пользователей и начисляет награды тем,
        у кого last_reward был более дня назад.

        Returns:
            dict: Статистика начислений
        """
        try:
            # Находим всех пользователей, у которых last_reward < вчерашний день
            yesterday = datetime.now() - timedelta(days=1)

            # Получаем всех пользователей с истекшей наградой
            stmt = (
                select(Money)
                .where((Money.last_reward < yesterday) | (Money.last_reward.is_(None)))
                .options(selectinload(Money.user))
            )
            result = await self.session.execute(stmt)
            money_list = result.scalars().all()

            if not money_list:
                logger.info("Нет пользователей для начисления ежедневной награды")
                return {"processed": 0, "users": []}

            processed_users = []
            total_scores_added = 0
            total_balance_added = 0

            # Начисляем награду каждому
            for money in money_list:
                # Рассчитываем сколько дней прошло
                days_passed = self._calculate_days_passed(money.last_reward)

                if days_passed > 0:
                    # Начисляем за каждый пропущенный день
                    scores_to_add = days_passed  # 1 score за день
                    balance_to_add = money.daily_reward * days_passed

                    # Обновляем значения
                    money.scores += scores_to_add
                    money.balance += balance_to_add
                    money.last_reward = datetime.now()

                    processed_users.append(
                        {
                            "user_id": money.user_id,
                            "username": money.user.username
                            if money.user
                            else str(money.user_id),
                            "days": days_passed,
                            "scores_added": scores_to_add,
                            "balance_added": balance_to_add,
                            "new_scores": money.scores,
                            "new_balance": money.balance,
                        }
                    )

                    total_scores_added += scores_to_add
                    total_balance_added += balance_to_add

                    logger.info(
                        f"Начислено пользователю {money.user_id}: "
                        f"{scores_to_add} score, {balance_to_add} руб. "
                        f"(пропущено дней: {days_passed})"
                    )

            # Сохраняем изменения
            await self.session.commit()

            logger.info(
                f"Ежедневное начисление завершено. "
                f"Обработано: {len(processed_users)} пользователей, "
                f"добавлено score: {total_scores_added}, "
                f"добавлено баланса: {total_balance_added}"
            )

            return {
                "processed": len(processed_users),
                "users": processed_users,
                "total_scores_added": total_scores_added,
                "total_balance_added": total_balance_added,
            }

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Ошибка при начислении ежедневных наград: {e}", exc_info=True)
            raise

    def _calculate_days_passed(self, last_reward: datetime) -> int:
        """Рассчитывает количество пропущенных дней"""
        if not last_reward:
            return 1  # Если никогда не получал награду

        now = datetime.now()
        days_diff = (now - last_reward).days

        # Если прошло больше дня, начисляем за все пропущенные дни
        # Но ограничиваем максимальное количество дней (например, 30)
        return min(days_diff, 30) if days_diff > 0 else 0


class DailyRewardScheduler:
    """Планировщик для ежедневных наград"""

    @staticmethod
    async def run_daily_rewards_job():
        """
        Задача для планировщика.
        Создает новую сессию для каждого выполнения.
        """
        logger.info("Запуск задачи ежедневного начисления наград...")

        # Создаем новую сессию для этой задачи
        async with async_session_factory() as session:
            try:
                reward_service = RewardService(session)
                result = await reward_service.process_daily_rewards()

                logger.info(
                    f"✅ Ежедневное начисление завершено. "
                    f"Награды получили {result['processed']} пользователей"
                )

                return result

            except Exception as e:
                logger.error(f"❌ Ошибка в задаче ежедневного начисления: {e}")
                raise
