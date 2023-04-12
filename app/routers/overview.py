from typing import List, Optional
from .. import models, schemas, oauth2
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
router = APIRouter(prefix="/overview", tags=["overview"])


@router.post('/')
def get_overview_expenses(filter: dict, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    group_id = filter.get('group_id')
    group_total_amount = db.query(models.ExpensesGroup).filter(
        models.ExpensesGroup.id == group_id).first()
    personal_total = db.query(models.ExpensesGroupMembers).filter(
        models.ExpensesGroupMembers.expenses_group_id == group_id, models.ExpensesGroupMembers.user_id == current_user.id).first()
    personal_total_round = round(personal_total.spent, 2)
    group_total_amount_round = round(group_total_amount.total_amount, 2)
    data = {
        'total_group_expense': group_total_amount_round,
        'total_personal_expense': personal_total_round
    }
    return data
