from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repository.money_repo import MoneyRepository
from database.models import Money


class MoneyService:
    """Сервис для работы с Money"""

    def __init__(self, session: AsyncSession):
        self.repo = MoneyRepository(session)

    async def get_money_info_by_user_id(self, telegram_id: int) -> Optional[Money]:
        """Получить Money получателя"""
        return await self.repo.get_by_telegram_id(telegram_id)

    async def add_score_by_money_id(
        self, money_id: int, scores: int
    ) -> Optional[Money]:
        """Добавление score в Money"""
        try:
            return await self.repo.add_score_by_money_id(money_id, scores)
        except Exception:
            return None

    async def reduce_score_by_money_id(
        self, money_id: int, scores: int
    ) -> Optional[Money]:
        """Убавление score в Money"""
        try:
            return await self.repo.reduce_score_by_money_id(money_id, scores)
        except Exception:
            return None

    async def update_daily_reward(
        self, money_id: int, new_reward: int
    ) -> Optional[Money]:
        """Обновить daily reward с проверками"""
        # Проверяем, что new_reward положительный
        if new_reward <= 0:
            raise ValueError("Daily reward must be positive")

        # Обновляем
        return await self.repo.update_daily_reward(money_id, new_reward)

    async def pay_out(self, money_id: int) -> Optional[Money]:
        """Выплатить. Значения score и balance сбрасываются до 0"""
        money = await self.repo.pay_out(money_id)
        if money is None:
            # Списание будет только, если баланс больше 0 и есть такой объект Money
            raise ValueError("Списание не удалось.")
        return money

    async def pay_out_partial(self, money_id: int, amount: int) -> Optional[Money]:
        """Выплатить частично."""
        updated_money = await self.repo.pay_out_partial(money_id, amount)
        if updated_money is None:
            raise ValueError("Списание не удалось.")
        return updated_money