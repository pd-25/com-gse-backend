from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

# T represents "Any Data Type" (e.g., a list of categories, a single user, etc.)
T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    meta: Optional[dict] = {}