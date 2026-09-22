from fastapi import APIRouter

from app.config import get_settings
from app.schemas.common import Health

router = APIRouter(tags=["health"])


@router.get("/health", response_model=Health)
async def health() -> Health:
    return Health(status="ok", version=get_settings().APP_VERSION)
