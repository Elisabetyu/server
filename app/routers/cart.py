# [file name]: routers/cart.py
from fastapi import APIRouter, Header, status, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import List

from ..utils import get_jwt_login, verify_jwt
from ..models.cart import CartUpdate, Cart
from ..database.cart import get_user_cart, update_cart_item, clear_user_cart, update_cart_item_amount
from ..database.user import get_user_id_by_username

router = APIRouter(
    prefix="/cart",
    tags=["Корзина"]
)
logger = logging.getLogger(__name__)

@router.get("", response_model=List[Cart])
@verify_jwt
async def get_cart(authorization: str = Header(...)):
    try:
        username = get_jwt_login(authorization)
        user_id = get_user_id_by_username(username)
        return get_user_cart(user_id)
    except Exception as e:
        logger.error(f"Ошибка получения корзины: {str(e)}")
        return JSONResponse(
            content={"message": "Ошибка получения корзины"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("", response_model=Cart)
@verify_jwt
async def update_cart(
    cart_data: CartUpdate,
    authorization: str = Header(...)
):
    try:
        username = get_jwt_login(authorization)
        user_id = get_user_id_by_username(username)
        return update_cart_item(user_id, cart_data.product_id, cart_data.amount)
    except Exception as e:
        logger.error(f"Ошибка обновления корзины: {str(e)}")
        return JSONResponse(
            content={"message": "Ошибка обновления корзины"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/update_amount")
@verify_jwt
async def update_cart_amount(
    cart_data: CartUpdate,
    authorization: str = Header(...)
):
    try:
        user_id = get_user_id_by_username(get_jwt_login(authorization))
        return update_cart_item_amount(user_id, cart_data.product_id, cart_data.amount)
    except Exception as e:
        logger.error(f"Ошибка обновления корзины: {str(e)}")
        return JSONResponse(
            content={"message": "Ошибка обновления корзины"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
@verify_jwt
async def clear_cart(authorization: str = Header(...)):
    try:
        username = get_jwt_login(authorization)
        user_id = get_user_id_by_username(username)
        clear_user_cart(user_id)
    except Exception as e:
        logger.error(f"Ошибка очистки корзины: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка очистки корзины"
        )