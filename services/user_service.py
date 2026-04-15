from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from repository.user_repo import UserRepository
from database.models import User


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str,
        first_name: str = None,
        last_name: str = None,
    ) -> User:
        """Получить или создать пользователя"""
        return await self.repo.create_or_update(
            telegram_id, username, first_name, last_name
        )

    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя"""
        return await self.repo.get_by_telegram_id(telegram_id)

    async def is_boss(self, telegram_id: int) -> bool:
        """Проверить, является ли пользователь боссом"""
        user = await self.repo.get_by_telegram_id(telegram_id)
        return user.is_boss if user else False

    async def get_all_bosses(self) -> List[User]:
        """Получить всех боссов"""
        return await self.repo.get_all_bosses()

    async def get_all_employees(self) -> List[User]:
        """Получить всех боссов"""
        return await self.repo.get_all_employees()

    async def promote_to_boss(self, telegram_id: int) -> bool:
        """Повысить пользователя до босса"""
        return await self.repo.set_boss_status(telegram_id, True)
