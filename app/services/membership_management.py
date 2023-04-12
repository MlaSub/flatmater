from .. import models, schemas, oauth2
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session


def add_member_to_group(db, user_id: int, group_id: int):
    group_upate = db.query(models.ExpensesGroup).filter(
        models.ExpensesGroup.id == group_id)
    current_members_new = group_upate.first()
    current_members = current_members_new.group_members
    if user_id not in current_members:
        current_members.append(user_id)
        dict = {"group_members": current_members}
        group_upate.update(dict)
        db.commit()


def removing_member_from_group(db, user_id: int, group_id: int):
    deleting_group_query = db.query(models.ExpensesGroup).filter(
        models.ExpensesGroup.id == group_id)
    deleting_group = deleting_group_query.first()
    deleting_group_members = deleting_group.group_members
    deleting_group_members.remove(user_id)
    dict = {"group_members": deleting_group_members}
    deleting_group_query.update(dict)
    db.commit()


def member_of_group(db, user_id, group_id) -> bool:
    membership = db.query(models.ExpensesGroupMembers).filter(
        models.ExpensesGroupMembers.expenses_group_id == group_id, models.ExpensesGroupMembers.user_id == user_id).first()

    if not membership:
        return False
    else:
        return True
