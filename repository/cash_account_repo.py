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
        new_cash_account.title = f"{title} #{new_cash_account.id}"
        await self.session.flush()

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

    async def update_account_currency(self, account_id: int, new_currency: str):
        stmt = (
            update(CashAccount)
            .where(CashAccount.id == account_id)
            .values(currency=new_currency)
            .returning(CashAccount)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_cash_account(self, cash_account_id: int) -> CashAccount | None:
        """
        Удаляет CashAccount по id.

        Возвращает:
            - удалённый объект CashAccount, если он существовал и был успешно удалён
            - None, если запись с таким id не найдена
        """
        stmt = select(CashAccount).where(CashAccount.id == cash_account_id)
        result = await self.session.execute(stmt)
        account = result.scalar_one_or_none()

        if account is None:
            return None

        await self.session.delete(account)
        await self.session.flush()

        return account
