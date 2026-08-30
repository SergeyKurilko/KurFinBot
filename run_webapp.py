"""
Запуск WebApp сервера
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "webapp.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Автоматический перезапуск при изменениях
        log_level="info"
    )