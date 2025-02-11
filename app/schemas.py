# app/schemas.py
from pydantic import BaseModel
from typing import Optional


# For token responses
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# For user authentication
class UserBase(BaseModel):
    username: str


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


# For inventory items
class InvItem(BaseModel):
    id: int
    item_name: str
    quantity: int

    class Config:
        from_attributes = True
