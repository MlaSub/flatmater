from .. import models, schemas, oauth2
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/")
def testing(item: dict, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_new = update_spent_amount(
        current_user.id, item.get('nesto'), db)
    return new_new


def current_amount_spent_group(id: int, group: int, db, mode) -> float:
    if mode == 'personal':
        expense_query = db.query(models.Expense).filter(
            models.Expense.owner_id == id, models.Expense.expenses_group_id == group).all()
    else:
        expense_query = db.query(models.Expense).filter(
            models.Expense.expenses_group_id == group).all()
    expenses_list = list(expense_query)
    all_expenses = 0
    for i in range(len(expenses_list)):
        all_expenses += expenses_list[i].amount
    return all_expenses


def update_spent_amount(id: int, group: int, db):
    new_spent_calc = current_amount_spent_group(id, group, db, 'personal')
    old_spent = db.query(models.ExpensesGroupMembers).filter(
        models.ExpensesGroupMembers.owner_id == id, models.ExpensesGroupMembers.expenses_group_id == group)
    dict = {"spent": new_spent_calc}
    old_spent.update(dict)
    db.commit()


def calculate_total_amount_group(id: int, group: int, db):
    new_total_amount = current_amount_spent_group(id, group, db, 'group')
    filtered_group = db.query(models.ExpensesGroup).filter(
        models.ExpensesGroup.id == group)
    dict = {"total_amount": new_total_amount}
    filtered_group.update(dict)
    db.commit()
