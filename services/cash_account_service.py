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

    async def get_cash_account_by_id(self, cash_account_id: int) -> CashAccount | None:
        return await self.repo.get_cash_account_by_id(cash_account_id)

    async def get_all_cash_accounts(self):
        return await self.repo.get_all_cash_accounts()

    async def update_account_title(self, account_id: int, new_title: str):
        return await self.repo.update_account_title(account_id=account_id, new_title=new_title)