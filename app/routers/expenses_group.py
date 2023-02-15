from sqlalchemy import false
from typing import List, Optional
from .. import models, schemas, oauth2
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/expenses-group", tags=["expenses_group"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.NewGroupOut)
def create_expenses_group(group: schemas.CreateExpensesGroup, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_expenses_group = models.ExpensesGroup(
        **group.dict(), owner_id=current_user.id, total_amount=0)
    db.add(new_expenses_group)
    db.commit()
    db.refresh(new_expenses_group)

    new_group_relation = models.ExpensesGroupMembers(
        expenses_group_id=new_expenses_group.id, owner_id=current_user.id, spent=0)
    db.add(new_group_relation)
    db.commit()
    db.refresh(new_group_relation)
    db.refresh(new_expenses_group)
    return (new_expenses_group)


@router.get("/")
def get_my_expenses_group(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    ids_of_groups = db.query(models.ExpensesGroup).join(
        models.ExpensesGroupMembers, models.ExpensesGroup.id == models.ExpensesGroupMembers.expenses_group_id, isouter=True).group_by(models.ExpensesGroup).filter(models.ExpensesGroupMembers.owner_id == current_user.id).all()
    return ids_of_groups


@router.get("/all")
def get_all_groups(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), search: Optional[str] = None):
    all_groups = db.query(models.ExpensesGroup).filter(
        models.ExpensesGroup.owner_id == current_user.id).order_by(models.ExpensesGroup.created_at.desc())
    if search == None:
        all_groups = all_groups.all()
        return (all_groups)
    else:
        all_groups_filtered = all_groups.filter(
            models.ExpensesGroup.title.ilike("%" + search + "%")).all()
        return (all_groups_filtered)


@ router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_expenses_group(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    expenses_group_delete = db.query(models.ExpensesGroup).filter(
        models.ExpensesGroup.owner_id == current_user.id, models.ExpensesGroup.id == id)
    expenses_group_delete.delete(synchronize_session=False)
    db.commit()
    return {"Success!"}


@ router.post("/member")
def add_member_expenses_group(item: schemas.AddMemberExpensesGroup, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_member = models.ExpensesGroupMembers(**item.dict())
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return {"message": "success"}
