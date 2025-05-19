from datetime import datetime, timezone, timedelta
from collections.abc import Callable
from functools import wraps
from typing import Optional

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError, PyJWTError as JWTError
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models.authorization import UserRole
from .static import SECRET_KEY, ALGORITHM

security = HTTPBearer()


def check_jwt(token: str) -> Optional[dict]:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует заголовок авторизации",
        )
    scheme, _, token = token.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат заголовка авторизации",
        )

    return jwt.decode(jwt=token, key=SECRET_KEY, algorithms=ALGORITHM)


def verify_jwt(f: Callable):
    @wraps(f)
    async def wrapper(
            *args,
            **kwargs
    ):
        """
        Функция-проверка JWT, передаваемого в заголовке Authorization.
        Ожидается формат: "Bearer <token>"
        """
        try:
            authorization = kwargs.get("authorization")
            check_jwt(authorization)
        except ExpiredSignatureError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Срок действия токена истек")
        except InvalidTokenError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Недействительный токен")
        return await f(*args, **kwargs)

    return wrapper


def create_jwt(login: str, role: UserRole, lifetime=timedelta(days=1)) -> str:
    return jwt.encode({
        "username": login,
        "role": role.value,
        "exp": datetime.now(tz=timezone.utc) + lifetime,
    }, SECRET_KEY, algorithm=ALGORITHM)


def     verify_admin(authorization: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = check_jwt(authorization.credentials)
        if payload.get("role") != UserRole.ADMIN.value:
            raise HTTPException(status_code=403, detail="Forbidden")
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_jwt_login(authorization: str) -> str:
    decoded_info: dict | None = check_jwt(authorization)

    if decoded_info is None or len(decoded_info) == 0:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный payload токена")

    return decoded_info["username"]
