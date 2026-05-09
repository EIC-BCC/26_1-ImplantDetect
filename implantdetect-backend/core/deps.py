from fastapi import Depends, HTTPException, status

from core.security import get_current_user, JWTPayload


def require_role(*roles: str):
    """Dependency factory que exige que o usuário tenha um dos roles especificados."""

    def dependency(user: JWTPayload = Depends(get_current_user)) -> JWTPayload:
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado.",
            )
        return user

    return Depends(dependency)


def require_admin() -> JWTPayload:
    return require_role("admin")
