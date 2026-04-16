from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from database.models import CashAccount
from repository.cash_account_repo import CashAccountRepository
from utils import cbr_courses

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
        cash_account = await self.repo.get_cash_account_by_id(cash_account_id)
        if cash_account and cash_account.currency == "USD":
            usd_course = None
            try:
                usd_course = await self.get_usd_course_from_cbr()
            except Exception:
                pass
            if usd_course and isinstance(usd_course, int):
                balance_in_rubles = cash_account.balance * usd_course
                cash_account.balance_in_rubles = balance_in_rubles
        return cash_account

    async def get_all_cash_accounts(self):
        return await self.repo.get_all_cash_accounts()

    async def update_account_title(self, account_id: int, new_title: str):
        return await self.repo.update_account_title(account_id=account_id, new_title=new_title)

    async def update_account_balance(self, account_id: int, new_balance: int):
        return await self.repo.update_account_balance(account_id, new_balance)

    async def update_account_currency(self, account_id: int, new_currency: str):
        return await self.repo.update_account_currency(account_id=account_id, new_currency=new_currency)

    async def delete_cash_account(self, cash_account_id: int):
        return await self.repo.delete_cash_account(cash_account_id)

    async def get_usd_course_from_cbr(self):
        return await cbr_courses.get_cbr_usd_course()

    async def get_consolidated_report(self) -> dict | None:
        all_cash_accounts: List[CashAccount] | [] = await self.repo.get_all_cash_accounts()
        total_rubles_balance = 0
        total_usd_balance = 0
        for cash_account in all_cash_accounts:
            if cash_account.currency == "RUB":
                total_rubles_balance += cash_account.balance
            elif cash_account.currency == "USD":
                total_usd_balance += cash_account.balance

        # Попытка получить курс валюты
        if total_usd_balance > 0:
            try:
                usd_course = await self.get_usd_course_from_cbr()
                if usd_course and isinstance(usd_course, int):
                    to_add = usd_course * total_usd_balance
                    total_rubles_balance += to_add
            except Exception:
                pass

        if all_cash_accounts:
            return {
                "all_cash_accounts": all_cash_accounts,
                "total_rubles_balance": total_rubles_balance,
                "total_usd_balance": total_usd_balance
            }
        return None