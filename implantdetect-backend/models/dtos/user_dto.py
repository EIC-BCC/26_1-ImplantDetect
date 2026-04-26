from pydantic import BaseModel

class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class UserUpdateRequest(BaseModel):
    user_id: int
    username: str | None = None
    email: str | None = None
    password: str | None = None
    
class UserTokenResponse(BaseModel):
    access_token: str
    token_type: str
    
    @classmethod
    def from_token(cls, token: str) -> 'UserTokenResponse':
        return cls(
            access_token=token,
            token_type="Bearer"
        )

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    active: bool

    @classmethod
    def from_orm(cls, user):
        return cls(
            user_id=user.id,
            username=user.username,
            email=user.email,
            active=bool(user.active)
        )