from typing import Literal
from pydantic import BaseModel, Field, field_validator


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("A senha deve conter ao menos um número.")
        if not any(c.isalpha() for c in v):
            raise ValueError("A senha deve conter ao menos uma letra.")
        return v


class UserUpdateRequest(BaseModel):
    # user_id é injetado pelo controller a partir do JWT — nunca aceito do body
    user_id: int = Field(exclude=True, default=0)
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: str | None = Field(default=None, max_length=254)
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not any(c.isdigit() for c in v):
            raise ValueError("A senha deve conter ao menos um número.")
        if not any(c.isalpha() for c in v):
            raise ValueError("A senha deve conter ao menos uma letra.")
        return v


class SetRoleRequest(BaseModel):
    role: Literal["user", "specialist", "admin"]


class SetActiveRequest(BaseModel):
    active: bool


class UserTokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role: str

    @classmethod
    def from_token(
        cls, token: str, user_id: int, username: str, role: str
    ) -> "UserTokenResponse":
        return cls(
            access_token=token,
            token_type="Bearer",
            user_id=user_id,
            username=username,
            role=role,
        )


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    active: bool

    @classmethod
    def from_orm(cls, user):
        return cls(
            user_id=user.id,
            username=user.username,
            email=user.email,
            role=getattr(user, "role", "user"),
            active=bool(user.active),
        )
