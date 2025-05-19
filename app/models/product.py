from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    cost: int
    icon: Optional[bytes] = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
