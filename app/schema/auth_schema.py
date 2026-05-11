from pydantic import BaseModel, Field, field_validator, EmailStr
import re


def normalize_username(value: str) -> str:
    value = value.strip().lower()
    if not re.fullmatch(
        r"^[A-Za-z0-9_]+$",
        value
    ):
        raise ValueError(
            "Username can only contain letters, numbers, and underscores"
        )
    return value


class RegisterUserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field()
    email: EmailStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        return normalize_username(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):

        value = value.strip()
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")

        return value


class UsernameLoginSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        return normalize_username(value)
    
class TokenSchema(BaseModel):
    token: str
    token_type: str
