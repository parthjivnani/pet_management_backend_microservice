from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    statusCode: int
    success: bool
    message: str
    result: Optional[Any] = None
