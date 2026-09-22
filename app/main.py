from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.errors import register_exception_handlers
from app.routers import chat, health, timeline

settings = get_settings()

app = FastAPI(title="Histor.ia API", version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health.router, prefix="/api")
app.include_router(timeline.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
