import hashlib
from logging import Logger

from psycopg2.extras import RealDictCursor
from psycopg2 import IntegrityError

from .connect import connect
from ..logger import configure_logs
from ..models.authorization import UserCredentials, UserRole
from ..utils import get_jwt_login


logger: Logger = configure_logs(__name__)


def insert_user(credentials: UserCredentials) -> bool:
    connection = connect()
    try:
        query = '''
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, %s);
                '''
        params = (
            credentials.username,
            hashlib.sha256(credentials.password.encode('utf-8')).hexdigest(),
            credentials.role.value
        )

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            connection.commit()
            return True

    except Exception as e:
        logger.error("An error excepted while adding user. Error: %s", e)
        raise
    finally:
        if connection:
            connection.close()


def get_user_role(username: str) -> UserRole:
    connection = connect()
    try:
        query = "SELECT role FROM users WHERE username = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            return UserRole(result[0]) if result else UserRole.USER
    except Exception as e:
        logger.error("Error getting user role: %s", e)
        raise
    finally:
        if connection:
            connection.close()


def identification(username: str) -> bool:
    connection = connect()

    try:
        query = '''
                SELECT CASE
                           WHEN EXISTS (SELECT 1
                                        FROM users
                                        WHERE username = %s)
                               THEN true
                           ELSE false
                           END AS is_valid;
                '''

        with connection.cursor() as cursor:
            cursor.execute(query, (username,))
            result: bool = cursor.fetchone()[0]

            return result
    except Exception as e:
        logger.error("An error excepted at identification process. Error: %s", e)
        raise
    finally:
        if connection:
            connection.close()


def authentication(credentials: UserCredentials) -> bool:
    connection = connect()

    try:
        query = '''
                SELECT CASE
                           WHEN EXISTS (SELECT 1
                                        FROM users
                                        WHERE username = %s
                                          AND password = %s)
                               THEN true
                           ELSE false
                           END AS is_valid;
                '''

        with connection.cursor() as cursor:
            cursor.execute(query,
                           (credentials.username, hashlib.sha256(credentials.password.encode('utf-8')).hexdigest()))
            result: bool = cursor.fetchone()[0]

            return result

    except Exception as e:
        logger.error("An error excepted at authentication process. Error: %s", e)
        raise
    finally:
        if connection:
            connection.close()

def get_user_id_by_username(username: str) -> int:
    connection = connect()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Пользователь не найден")
            return result['id']
    except Exception as e:
        logger.error(f"Ошибка получения user_id: {e}")
        raise
    finally:
        if connection:
            connection.close()

def get_user_profile(authorization: str) -> dict:
    """Получение профиля пользователя с фиктивными данными"""
    try:
        username = get_jwt_login(authorization)
        # Возвращаем фиктивные данные даже если нет соединения с БД
        return {
            "username": username,
            "email": f"{username}@example.com",
            "phone": "+7(999)-99-99",
            "orders_count": 5,
            "membership": "Золотой клиент"
        }
    except:
        # Резервный вариант если возникла ошибка авторизации
        return {
            "username": "guest",
            "email": "guest@example.com",
            "phone": "Не указан",
            "orders_count": 0,
            "membership": "Regular"
        }


