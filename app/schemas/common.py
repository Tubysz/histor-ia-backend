from pydantic import BaseModel


class Health(BaseModel):
    status: str
    version: str


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
