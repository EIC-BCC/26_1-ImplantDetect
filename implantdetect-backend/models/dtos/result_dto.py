from typing import Any
from pydantic import BaseModel


class Result(BaseModel):
    success: bool
    message: str | None = None
    data: dict[str, Any] | None = None

    @classmethod
    def ok(cls, message: str | None = None, data: dict[str, Any] | None = None) -> dict:
        return cls(success=True, message=message, data=data).to_dict()

    @classmethod
    def error(
        cls, message: str | None = None, data: dict[str, Any] | None = None
    ) -> dict:
        return cls(success=False, message=message, data=data).to_dict()

    def to_dict(self) -> dict:
        return {"success": self.success, "message": self.message, "data": self.data}
