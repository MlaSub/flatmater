from typing import Optional
from pydantic import BaseModel, EmailStr, conint, Field
from xmlrpc.client import boolean
from datetime import date, datetime

from app.database import Base


class SingleItem(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float
    expenses_group_id: int
    payment_module: str
    payment_user_id: int


class User(BaseModel):
    name: str
    surname: str
    password: str
    email: EmailStr


class UserOut(BaseModel):
    name: str
    surname: str
    id: int
    email: EmailStr
    member: Optional[boolean] = None

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class CreateExpensesGroup(BaseModel):
    title: str


class AddMemberExpensesGroup(BaseModel):
    user_id: int
    expenses_group_id: int
    spent: int = 0
    real_expense: int = 0


class DeleteMemberExpenseGroup(BaseModel):
    user_id: int
    expenses_group_id: int


class NewGroupOut(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True
