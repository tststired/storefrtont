from pydantic import BaseModel
from typing import Optional, Literal

class ItemOut(BaseModel):
    id: int
    title: str
    price: float
    category: Literal["mice", "mousepads"]
    image_filename: Optional[str] = None
    sold: bool
    created_at: str
