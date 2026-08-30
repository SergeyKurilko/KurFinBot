import os
from dataclasses import dataclass


@dataclass
class BotConfig:
    """Конфигурация бота"""
    token: str
    # admin_ids: list[int]
    proxy: str
    environment: str = "development"  # development, production
    webapp_url: str = "http://localhost:8000"

    @classmethod
    def from_env(cls) -> "BotConfig":
        """Загрузка конфигурации из переменных окружения"""
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("BOT_TOKEN not found in environment")
        proxy = os.getenv("POLAND_PROXY_URL")
        if not proxy:
            raise ValueError("POLAND_PROXY_URL not found in environment")
        # admin_ids_str = os.getenv("ADMIN_IDS", "")
        # admin_ids = [int(id_) for id_ in admin_ids_str.split(",") if id_]
        webapp_url = os.getenv("WEBAPP_URL", "http://localhost:8000")
        environment = os.getenv("ENVIRONMENT", "development")

        return cls(token=token, environment=environment, proxy=proxy, webapp_url=webapp_url)

    @classmethod
    def from_file(cls, path: str) -> "BotConfig":
        """Загрузка из файла (например, для тестов)"""
        # Можно загружать из JSON/YAML
        pass


# Создаем глобальный экземпляр конфига
config = BotConfig.from_env()
