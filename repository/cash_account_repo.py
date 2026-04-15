from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import CashAccount


class CashAccountRepository:
    "Репозиторий для работы с CashAccount"

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_new_account(self, title: str, balance: int, currency: str = "RUB"):
        new_cash_account = CashAccount(title=title, balance=balance, currency=currency)
        self.session.add(new_cash_account)
        await self.session.flush()
        await self.session.refresh(new_cash_account)
        return new_cash_account

    async def get_cash_account_by_id(self, cash_account_id) -> CashAccount | None:
        stmt = select(CashAccount).where(CashAccount.id == cash_account_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_cash_accounts(self):
        stmt = select(CashAccount).order_by(CashAccount.id)
        return (await self.session.execute(stmt)).scalars().all()

    async def update_account_title(
        self,
        account_id: int,
        new_title: str,
    ) -> CashAccount | None:
        stmt = (
            update(CashAccount)
            .where(CashAccount.id == account_id)
            .values(title=new_title)
            .returning(CashAccount)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_account_balance(self, account_id: int, new_balance: int):
        stmt = (
            update(CashAccount)
            .where(CashAccount.id == account_id)
            .values(balance=new_balance)
            .returning(CashAccount)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
