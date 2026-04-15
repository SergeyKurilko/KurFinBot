from sqlalchemy.ext.asyncio import AsyncSession
from database.models import CashAccount
from repository.cash_account_repo import CashAccountRepository


class CashAccountService:
    """Сервис для работы с CashAccount"""
    def __init__(self, session: AsyncSession):
        self.repo = CashAccountRepository(session)

    async def create_new_account(
            self,
            title: str,
            balance: int,
            currency: str = "RUB"
    ) -> CashAccount | None:
        """Сервис для создания нового CashAccount"""
        try:
            return await self.repo.create_new_account(title, balance, currency)
        except Exception as e:
            return None