from pydantic import BaseModel
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserCredentials(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.USER


class UserResponse(BaseModel):
    username: str
    role: UserRole
