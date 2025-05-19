# [file name]: database/cart.py
from typing import List
from logging import Logger
from psycopg2 import OperationalError, InterfaceError
from psycopg2.extras import RealDictCursor
from .connect import connect
from ..logger import configure_logs
from ..models.cart import Cart

logger: Logger = configure_logs(__name__)


def get_user_cart(user_id: int) -> List[Cart]:
    """Получает содержимое корзины пользователя"""
    logger.info(f"Получение корзины для пользователя {user_id}")
    conn = None
    try:
        conn = connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                    SELECT c.id, \
                           c.product_id, \
                           c.amount, \
                           c.user_id, \
                           p.name, \
                           p.cost, \
                           CASE \
                               WHEN p.icon IS NOT NULL \
                                   THEN encode(p.icon::bytea, 'base64') \
                               ELSE NULL \
                               END as icon
                    FROM cart c
                             JOIN products p ON c.product_id = p.id
                    WHERE c.user_id = %s
                    ORDER BY p.name \
                    """
            cur.execute(query, (user_id,))
            results = cur.fetchall()
            return [Cart(**row) for row in results]

    except (OperationalError, InterfaceError) as e:
        logger.error(f"Ошибка соединения: {e}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении корзины: {e}")
        raise
    finally:
        if conn:
            conn.close()


def clear_user_cart(user_id: int):
    logger.info(f"Очистка корзины для пользователя {user_id}")
    conn = None
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
            conn.commit()
    except Exception as e:
        logger.error(f"Ошибка очистки корзины: {e}")
        raise
    finally:
        if conn:
            conn.close()


def update_cart_item_amount(user_id: int, product_id: int, amount: int) -> int | None:
    logger.info(f"Изменение количества товара с id {product_id} у пользователя с id {user_id}")
    conn = None
    try:
        conn = connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                    INSERT INTO cart (user_id, product_id, amount)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, product_id)
                        DO UPDATE SET amount = EXCLUDED.amount
                    RETURNING amount
                    """
            cur.execute(query, (user_id, product_id, amount))

            result = cur.fetchone()
            conn.commit()

            if not result:
                return None

            return result['amount']
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Ошибка соединения: {e}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении корзины: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def update_cart_item(user_id: int, product_id: int, amount: int) -> Cart:
    logger.info(f"Обновление корзины для пользователя {user_id}")
    conn = None
    try:
        conn = connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Удаляем запись если количество <= 0
            if amount <= 0:
                query = """
                        DELETE \
                        FROM cart
                        WHERE user_id = %s \
                          AND product_id = %s
                        RETURNING *
                        """
                cur.execute(query, (user_id, product_id))
            else:
                # Используем UPSERT (INSERT ON CONFLICT UPDATE)
                query = """
                        INSERT INTO cart (user_id, product_id, amount)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, product_id)
                            DO UPDATE SET amount = EXCLUDED.amount
                        RETURNING *
                        """
                cur.execute(query, (user_id, product_id, amount))

            result = cur.fetchone()
            conn.commit()

            if not result:
                return None

            # Получаем полную информацию о продукте
            product_query = """
                            SELECT id, \
                                   name, \
                                   cost, \
                                   CASE \
                                       WHEN icon IS NOT NULL \
                                           THEN encode(icon::bytea, 'base64') \
                                       ELSE NULL \
                                       END as icon
                            FROM products \
                            WHERE id = %s \
                            """
            cur.execute(product_query, (product_id,))
            product_info = cur.fetchone()

            return Cart(
                id=result['id'],
                product_id=product_id,
                user_id=user_id,
                amount=result['amount'],
                name=product_info['name'],
                cost=product_info['cost'],
                icon=product_info['icon']
            )
    except (OperationalError, InterfaceError) as e:
        logger.error(f"Ошибка соединения: {e}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении корзины: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()