from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class ItemOut(BaseModel):
    id: str
    title: str
    price: float
    category: Literal["mice", "mousepads"]
    image_filename: Optional[str] = None
    sold: bool
    created_at: datetime
