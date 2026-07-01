from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class CategorySchema(BaseModel):
    id: int
    slug: str
    created_at: Optional[datetime] = None
    
    
class CategoryFilterSchema(BaseModel):
    limit: Optional[int] = 30
    
class CategoryListResponse(CategorySchema):
    name: str
    image: Optional[str] = None
    thumbnail_image: Optional[str] = None
    total_products: int = 0
    

    