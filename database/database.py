import datetime
import zoneinfo
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from database.models import User, Money, Base

PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DB_PATH = PROJECT_ROOT / "kurfinbot.db"

# Создаем URL для БД
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Контекстный менеджер для сессии"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()  # Автокоммит если не было ошибок
        except Exception:
            await session.rollback()  # Откат при ошибке
            raise
        finally:
            await session.close()  # Закрываем сессию

# ДЛЯ FASTAPI: Dependency Injection
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сессии для FastAPI (используется с Depends)"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        # Use run_sync to execute the synchronous create_all method
        await conn.run_sync(Base.metadata.create_all)

    # # Always dispose of the engine in async environments to close connections properly
    # await engine.dispose()
    async with async_session_factory() as session:
        # Стартовые пользователи:
        start_users = os.getenv("START_USERS")
        start_users_list = start_users.split(",") # example: <123456987|Username|is_boss>
        for start_user in start_users_list:
            user_id = start_user.split("|")[0]
            user_name = start_user.split("|")[1]
            is_boss = start_user.split("|")[-1]
            is_boss = True if is_boss.lower() == "true" else False
            # Проверяем, существует ли пользователь
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            exists = result.scalar_one_or_none()
            if not exists:
                user = User(id=user_id, username=user_name, is_boss=is_boss)
                session.add(user)
        await session.commit()

        # Стартовые кошельки
        for start_user in start_users_list:
            user_id = start_user.split("|")[0]
            is_boss = start_user.split("|")[-1]
            is_boss = True if is_boss.lower() == "true" else False
            if not is_boss:
                # Проверяем, существует ли кошелек
                stmt = select(Money).where(Money.user_id == user_id)
                result = await session.execute(stmt)
                exists = result.scalar_one_or_none()
                if not exists:
                    money = Money(
                        balance=0,
                        scores=0,
                        daily_reward=175,
                        last_reward=datetime.datetime.now(ZoneInfo("Europe/Moscow")),
                        user_id=user_id,
                    )
                    session.add(money)
        await session.commit()



async def dispose_engine():
    await engine.dispose()

