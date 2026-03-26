from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """Standard API response matching Node backend: statusCode, success, message, result."""
    statusCode: int
    success: bool
    message: str
    result: Optional[Any] = None
