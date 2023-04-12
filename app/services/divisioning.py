from .. import models, schemas, oauth2
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session


def equal_cost_dividing(amount: float, group_id: int, db, expense_id: int, module: str, paying_user: int):
    current_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id)
    if module == "self":
        cost_structure = {paying_user: amount}
        current_expense.update({"cost_division": cost_structure})
        db.commit()
    elif module == "equalsomeone":
        current_group = db.query(models.ExpensesGroup).filter(
            models.ExpensesGroup.id == group_id)
        current_members_list = current_group.first().group_members
        list_of_users_expenses = {}
        amount_per_user = round(amount / len(current_members_list), 3)
        for i in range(len(current_members_list)):
            list_of_users_expenses.update(
                {current_members_list[i]: amount_per_user})
        current_expense.update({"cost_division": list_of_users_expenses})
        db.commit()


def payment_dividing(amount: float, user_paying: int, db, expense_id: int):
    current_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id)
    payment_stucture = {user_paying: amount}
    current_expense.update({"payment_division": payment_stucture})
    db.commit()
