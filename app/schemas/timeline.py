from pydantic import BaseModel


class Era(BaseModel):
    id: str
    nome: str
    periodo: str
    descricao: str


class MarcoResumo(BaseModel):
    id: str
    ano: int
    titulo: str
    era: str
    resumo: str
    tags: list[str]


class MarcoCompleto(MarcoResumo):
    descricao: str
    tecnica: str
    fontes: list[str]
