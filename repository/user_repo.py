from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Money


class UserRepository:
    """Репозиторий для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        result = await self.session.execute(select(User).where(User.id == telegram_id))
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        telegram_id: int,
        username: str,
    ) -> User:
        """Создать или обновить пользователя"""
        user = await self.get_by_telegram_id(telegram_id)

        if user:
            user.username = username
            await self.session.commit()
            await self.session.refresh(user)
            return user
        else:
            user = User(
                id=telegram_id,
                username=username,
                is_boss=False,
                is_active=True,
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user

    async def get_all_bosses(self) -> List[User]:
        """Получить всех боссов"""
        result = await self.session.execute(
            select(User).where(User.is_boss == True, User.is_active == True)
        )
        return result.scalars().all()

    async def get_all_employees(self) -> List[User]:
        """Получить всех сотрудников"""
        result = await self.session.execute(
            select(User).where(User.is_boss == False)
        )
        return result.scalars().all()

    async def set_boss_status(self, user_id: int, is_boss: bool) -> bool:
        """Установить статус босса"""
        result = await self.session.execute(
            update(User).where(User.id == user_id).values(is_boss=is_boss)
        )
        await self.session.commit()
        return result.rowcount > 0
