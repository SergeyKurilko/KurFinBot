from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from database.database import get_db_session
from repository.user_repo import UserRepository
from repository.money_repo import MoneyRepository
from services.user_service import UserService
from services.money_service import MoneyService

# --- Репозитории ---
async def get_user_repo(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    return UserRepository(session)

async def get_money_repo(
    session: AsyncSession = Depends(get_db_session)
) -> MoneyRepository:
    return MoneyRepository(session)

# --- Сервисы ---
async def get_user_service(
    repo: UserRepository = Depends(get_user_repo)
) -> UserService:
    return UserService(repo)

async def get_money_service(
    repo: MoneyRepository = Depends(get_money_repo)
) -> MoneyService:
    return MoneyService(repo)