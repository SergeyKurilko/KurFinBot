from pydantic import BaseModel, Field, field_validator
from typing import Optional

class UpdateAccountRequest(BaseModel):
    balance: Optional[float] = Field(None, description="Новый баланс счета")
    title: Optional[str] = Field(None, description="Новое название счета")
    currency: Optional[str] = Field(None, description="Новая валюта")

    @field_validator("balance")
    @classmethod
    def check_balance(cls, v):
        if v is not None and v < 0:
            raise ValueError("Баланс не может быть отрицательным!")
        return v

    @field_validator("title")
    @classmethod
    def check_title(cls, v):
        if v is not None:
            if len(v) < 3 or len(v) > 55:
                raise ValueError("Название должно быть от 3 до 55 символов.")
        return v

    @field_validator("currency")
    @classmethod
    def check_currency(cls, v):
        if v is not None and v not in ["USD", "RUB"]:
            raise ValueError("Должно быть USD или RUB")
        return v