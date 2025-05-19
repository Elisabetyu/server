from typing import Optional
from pydantic import BaseModel

class CartUpdate(BaseModel):
    product_id: int
    amount: int

class CartBase(BaseModel):
    product_id: int
    amount: int

class CartCreate(CartBase):
    pass

class Cart(CartBase):
    id: int
    user_id: int
    name: str  # Из таблицы products
    cost: int  # Из таблицы products
    icon: Optional[str] = None
