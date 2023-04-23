# from typing import List, Optional
from .. import models, schemas, oauth2
from fastapi import Depends, APIRouter
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
    pesronal_total_expense_share = round(personal_total.real_expense, 2)
    data = {
        'total_group_expense': group_total_amount_round,
        'total_personal_expense': personal_total_round,
        'pesronal_total_expense_share': pesronal_total_expense_share

    }
    return data


@router.post('/debt')
def get_overview_expenses_debt(filter: dict, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    group_id = filter.get('group_id')
    group_member_queried = db.query(models.ExpensesGroupMembers.debt_distribution).filter(
        models.ExpensesGroupMembers.expenses_group_id == group_id, models.ExpensesGroupMembers.user_id == current_user.id).first()[0]

    try:
        debtors = [{'id': user.id, 'name': user.name + ' ' + user.surname, 'amount': group_member_queried['debtors'].get(str(user.id))}
                   for user in db.query(models.User.id, models.User.name, models.User.surname).filter(models.User.id.in_(list(group_member_queried.get('debtors', {}).keys()))).all()]

        owing = [{'id': user.id, 'name': user.name + ' ' + user.surname, 'amount': group_member_queried['owing'].get(str(user.id))}
                 for user in db.query(models.User.id, models.User.name, models.User.surname).filter(models.User.id.in_(list(group_member_queried.get('owing', {}).keys()))).all()]

    except KeyError:
        debtors = []
        owing = []

    return {'debtors': debtors, 'owing': owing}
