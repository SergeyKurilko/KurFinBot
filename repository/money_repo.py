from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Money


class MoneyRepository:
    """Репозиторий для работы с Money"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Money]:
        """Получить пользователя по Telegram ID"""
        result = await self.session.execute(
            select(Money).where(Money.user_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def add_score_by_money_id(self, money_id: int, scores) -> Optional[Money]:
        stmt = (
            update(Money)
            .where(Money.id == money_id)
            .values(
                scores=Money.scores + scores,
                balance=Money.balance + (scores * Money.daily_reward),
            )
            .returning(Money)
        )
        result = await self.session.execute(stmt)
        updated_money = result.scalar_one_or_none()
        return updated_money

    async def reduce_score_by_money_id(self, money_id: int, scores) -> Optional[Money]:
        """Списание score и balance. Допускается отрицательное значение!"""
        stmt = (
            update(Money)
            .where(Money.id == money_id)
            .values(
                scores=Money.scores - scores,
                balance=Money.balance - (scores * Money.daily_reward),
            )
            .returning(Money)
        )
        result = await self.session.execute(stmt)
        updated_money = result.scalar_one_or_none()
        return updated_money

    async def update_daily_reward(
        self, money_id: int, new_reward: int
    ) -> Optional[Money]:
        """Обновить daily reward"""
        stmt = (
            update(Money)
            .where(Money.id == money_id)
            .values(daily_reward=new_reward)
            .returning(Money)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()


    async def pay_out(self, money_id: int) -> Optional[Money]:
        """Выплатить. Сбрасывает scores и balance в 0.
        Выплата возможна только если баланс не отрицательный.
        """
        stmt = (
            update(Money)
            .where(Money.id == money_id)
            .where(Money.balance > 0)  # Только положительный баланс
            .values(scores=0, balance=0)
            .returning(Money)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()
