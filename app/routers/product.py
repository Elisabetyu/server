import logging

from fastapi import APIRouter, status, Header, Depends
from fastapi.responses import JSONResponse
from psycopg2 import errors

from ..utils import verify_jwt, verify_admin
from ..models.product import Product, ProductCreate
from ..database.product import (
    get_all_products,
    get_product,
    create_product,
    update_product,
    delete_product
)

router = APIRouter(
    prefix="/products",
    tags=["Управление товарами"]
)


@router.get("", response_model=list[Product])
@verify_jwt
async def read_products(authorization: str = Header(..., description="JWT токен в формате Bearer <token>")):
    try:
        return get_all_products()
    except Exception as e:
        logging.error(e)
        return JSONResponse(
            content={"message": "Ошибка получения товаров"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{product_id}", response_model=Product)
@verify_jwt
async def read_product(product_id: int,
                       authorization: str = Header(..., description="JWT токен в формате Bearer <token>")):
    try:
        product = get_product(product_id)
        if not product:
            return JSONResponse(
                content={"message": "Товар не найден"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        return product
    except Exception as e:
        logging.error(e)
        return JSONResponse(
            content={"message": "Ошибка получения товара"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("", response_model=Product, dependencies=[Depends(verify_admin)])
async def create_new_product(product: ProductCreate,
                             authorization: str = Header(..., description="JWT токен в формате Bearer <token>")):
    try:
        return create_product(product)
    except errors.UniqueViolation:
        return JSONResponse(
            content={"message": "Товар с таким именем уже существует"},
            status_code=status.HTTP_409_CONFLICT
        )
    except Exception as e:
        logging.error(e)
        return JSONResponse(
            content={"message": "Ошибка создания товара"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/{product_id}", response_model=Product, dependencies=[Depends(verify_admin)])
async def update_existing_product(product_id: int, product: ProductCreate,
                                  authorization: str = Header(..., description="JWT токен в формате Bearer <token>")):
    try:
        updated_product = update_product(product_id, product)
        if not updated_product:
            return JSONResponse(
                content={"message": "Товар не найден"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        return updated_product
    except errors.UniqueViolation:
        return JSONResponse(
            content={"message": "Товар с таким именем уже существует"},
            status_code=status.HTTP_409_CONFLICT
        )
    except Exception as e:
        logging.error(e)
        return JSONResponse(
            content={"message": "Ошибка обновления товара"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/{product_id}", dependencies=[Depends(verify_admin)])
async def delete_existing_product(product_id: int,
                                  authorization: str = Header(..., description="JWT токен в формате Bearer <token>")):
    try:
        success = delete_product(product_id)
        if not success:
            return JSONResponse(
                content={"message": "Товар не найден"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        return JSONResponse(
            content={"message": "Товар успешно удален"},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logging.error(e)
        return JSONResponse(
            content={"message": "Ошибка удаления товара"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
