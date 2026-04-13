from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: str
    code: int


class SuccessResponse(BaseModel):
    status: str = "ok"
    data: Any
