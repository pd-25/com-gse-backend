from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

# T represents "Any Data Type" (e.g., a list of categories, a single user, etc.)
T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    meta: Optional[dict] = Field(default_factory=dict)
