import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from psycopg2 import errors

from ..database.user import identification, authentication, insert_user, get_user_role
from ..utils import create_jwt
from ..models.authorization import UserCredentials

router = APIRouter(
    prefix="/auth",
    tags=["Изменение учетной записи пользователя"]
)


@router.post("/registration")
def registration(credentials: UserCredentials) -> JSONResponse:
    try:
        if identification(credentials.username):
            return JSONResponse(content={'message': 'Такой логин уже зарегистрирован'},
                                status_code=status.HTTP_409_CONFLICT)

        insert_user(credentials)

        return JSONResponse(
            content={
                'message': 'Пользователь успешно зарегистрирован',
                'token': create_jwt(credentials.username, credentials.role),
                'role': 0b10
            },
            status_code=status.HTTP_201_CREATED
        )
    except errors.UniqueViolation:
        return JSONResponse(content={'message': 'Логин занят'},
                            status_code=status.HTTP_409_CONFLICT)
    except Exception as e:
        logging.error(e)
        return JSONResponse(content={'message': 'Ошибка сервера'},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/login")
def login(credentials: UserCredentials) -> JSONResponse:
    try:
        if not identification(credentials.username):
            return JSONResponse(content={'message': 'Не существует пользователя с таким логином'},
                                status_code=status.HTTP_401_UNAUTHORIZED)

        if not authentication(credentials):
            return JSONResponse(content={'valid': False,
                                         'message': 'Не правильный пароль'},
                                status_code=status.HTTP_401_UNAUTHORIZED)

        # Получаем роль пользователя из БД
        user_role = get_user_role(credentials.username)

        return JSONResponse(
            content={
                'message': 'Успешный вход',
                'token': create_jwt(credentials.username, user_role)
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logging.error(e)
        return JSONResponse(content={'message': 'Ошибка сервера'},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)