from .database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy import Column, Float, Integer, String, TIMESTAMP, ForeignKey, ARRAY, null, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String)
    cost_division = Column(JSON)
    payment_division = Column(JSON)
    payment_module = Column(String)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User")
    expenses_group_id = Column(Integer, ForeignKey(
        "expenses_group.id", ondelete="CASCADE"))
    owner = relationship("ExpensesGroup")


class ExpensesGroup(Base):
    __tablename__ = "expenses_group"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    total_amount = Column(Float)
    group_members = Column(MutableList.as_mutable(ARRAY(Integer)))
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User")


class ExpensesGroupMembers(Base):
    __tablename__ = "expenses_group_members"
    expenses_group_id = Column(Integer, ForeignKey(
        "expenses_group.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    spent = Column(Float)
    real_expense = Column(Float)
