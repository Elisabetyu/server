from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from ..database.user import get_user_profile, logger
from ..utils import get_jwt_login

router = APIRouter(
    prefix="/profile",
    tags=["Профиль пользователя"]
)

class UserProfileResponse(BaseModel):
    username: str
    email: str
    phone: str
    orders_count: int
    membership: str

@router.get("", response_model=UserProfileResponse)
def get_profile(authorization: str = Header(...)):
    try:
        return get_user_profile(authorization)
    except Exception as e:
        logger.error(f"Ошибка получения профиля: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")