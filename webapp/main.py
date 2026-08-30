import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from database.database import init_db, dispose_engine
from webapp.api import auth, test, cash

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом WebApp"""
    # Старт
    logger.info("🚀 WebApp сервер запускается...")
    await init_db()
    logger.info("✅ База данных готова")
    yield
    # Шатдаун
    logger.info("🛑 WebApp сервер останавливается...")
    await dispose_engine()
    logger.info("Соединения с БД закрыты")

# Создаем приложение
app = FastAPI(
    title="KurfinBot WebApp",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS (для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничьте
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем статику (фронтенд)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Подключаем API роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(test.router, prefix="/api/test", tags=["test"])
app.include_router(cash.router, prefix="/api/cash", tags=["cash"])

# Корневой путь - отдаем index.html
@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "WebApp is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "webapp"}