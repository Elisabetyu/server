from typing import Optional, List
from logging import Logger

from psycopg2 import OperationalError, InterfaceError
from psycopg2.extras import RealDictCursor
from psycopg2.errors import UniqueViolation

from .connect import connect
from ..logger import configure_logs
from ..models.product import Product, ProductCreate

__all__: List[str] = [
    "get_all_products",
    "get_product",
    "create_product",
    "update_product",
    "delete_product"
]
logger: Logger = configure_logs(__name__)


def get_all_products() -> List[Product]:
    logger.info("Начало получения всех продуктов из базы данных.")
    conn = None
    try:
        conn = connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT 
                    id, 
                    name,   
                    COALESCE(description, '') as description, 
                    cost,
                    CASE 
                        WHEN icon IS NOT NULL 
                        THEN encode(icon::bytea, 'base64') 
                        ELSE NULL 
                    END as icon 
                FROM products
            """
            cur.execute(query)
            result = cur.fetchall()
            logger.info("Количество полученных продуктов: %s", len(result))
            return [Product(**row) for row in result]
    except (OperationalError, InterfaceError) as e:
        logger.error("Ошибка соединения: %s", e)
        raise
    except Exception as e:
        logger.error("Ошибка при выполнении запроса: %s", e)
        raise
    finally:
        if conn:
            conn.close()


def get_product(product_id: int) -> Optional[Product]:
    logger.info("Начало получения продукта по ID %s", product_id)
    conn = None
    try:
        conn = connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT 
                    id, 
                    name, 
                    COALESCE(description, '') as description, 
                    cost,
                    CASE 
                        WHEN icon IS NOT NULL 
                        THEN encode(icon::bytea, 'base64') 
                        ELSE NULL 
                    END as icon 
                FROM products 
                WHERE id = %s
            """
            cur.execute(query, (product_id,))
            result = cur.fetchone()
            logger.info("Продукт %s %s", product_id, "найден" if result else "не найден")
            return Product(**result) if result else None
    except (OperationalError, InterfaceError) as e:
        logger.error("Ошибка соединения: %s", e)
        raise
    except Exception as e:
        logger.error("Ошибка при выполнении запроса: %s", e)
        raise
    finally:
        if conn:
            conn.close()


def create_product(product: ProductCreate) -> Product:
    logger.info("Начало создания продукта с именем %s", product.name)
    conn = None
    try:
        conn = connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                INSERT INTO products (name, description, cost, icon)
                VALUES (%s, %s, %s, %s)
                RETURNING 
                    id, 
                    name, 
                    COALESCE(description, '') as description, 
                    cost,
                    CASE 
                        WHEN icon IS NOT NULL 
                        THEN encode(icon::bytea, 'base64') 
                        ELSE NULL 
                    END as icon
            """
            params = (
                product.name,
                product.description,
                product.cost,
                product.icon
            )
            cur.execute(query, params)
            conn.commit()
            result = cur.fetchone()
            logger.info("Продукт успешно создан с ID %s", result['id'])
            return Product(**result)
    except UniqueViolation as e:
        logger.error("Ошибка: имя продукта должно быть уникальным")
        if conn:
            conn.rollback()
        raise
    except (OperationalError, InterfaceError) as e:
        logger.error("Ошибка соединения: %s", e)
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        logger.error("Ошибка при создании продукта: %s", e)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def update_product(product_id: int, product: ProductCreate) -> Optional[Product]:
    logger.info("Начало обновления продукта с ID %s", product_id)
    conn = None
    try:
        conn = connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                UPDATE products
                SET name = %s,
                    description = %s,
                    cost = %s,
                    icon = %s
                WHERE id = %s
                RETURNING 
                    id, 
                    name, 
                    COALESCE(description, '') as description, 
                    cost,
                    CASE 
                        WHEN icon IS NOT NULL 
                        THEN encode(icon::bytea, 'base64') 
                        ELSE NULL 
                    END as icon
            """
            params = (
                product.name,
                product.description,
                product.cost,
                product.icon,
                product_id
            )
            cur.execute(query, params)
            conn.commit()
            result = cur.fetchone()
            if result:
                logger.info("Продукт с ID %s успешно обновлен", product_id)
                return Product(**result)
            else:
                logger.info("Продукт с ID %s не найден", product_id)
                return None
    except UniqueViolation as e:
        logger.error("Ошибка: имя продукта должно быть уникальным")
        if conn:
            conn.rollback()
        raise
    except (OperationalError, InterfaceError) as e:
        logger.error("Ошибка соединения: %s", e)
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        logger.error("Ошибка при обновлении продукта: %s", e)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def delete_product(product_id: int) -> bool:
    logger.info("Начало удаления продукта с ID %s", product_id)
    conn = None
    try:
        conn = connect()
        with conn.cursor() as cur:
            query = "DELETE FROM products WHERE id = %s"
            cur.execute(query, (product_id,))
            conn.commit()
            deleted = cur.rowcount > 0
            logger.info("Продукт с ID %s %sудален", product_id, "" if deleted else "не ")
            return deleted
    except (OperationalError, InterfaceError) as e:
        logger.error("Ошибка соединения: %s", e)
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        logger.error("Ошибка при удалении продукта: %s", e)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()