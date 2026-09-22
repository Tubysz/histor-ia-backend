from fastapi import APIRouter

from app.errors import NotFoundError
from app.schemas.timeline import Era, MarcoCompleto, MarcoResumo
from app.services import knowledge

router = APIRouter(tags=["timeline"])


@router.get("/eras", response_model=list[Era])
async def list_eras() -> list[dict]:
    return knowledge.list_eras()


@router.get("/timeline", response_model=list[MarcoResumo])
async def list_timeline(era: str | None = None) -> list[dict]:
    return knowledge.list_timeline(era=era)


@router.get("/timeline/{marco_id}", response_model=MarcoCompleto)
async def get_marco(marco_id: str) -> dict:
    marco = knowledge.get_marco(marco_id)
    if marco is None:
        raise NotFoundError("Marco não encontrado.")
    return marco
