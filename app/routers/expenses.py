from typing import List, Optional
from .. import models, schemas, oauth2
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from ..services import calculation_expenses_per_group_per_member


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/items", status_code=status.HTTP_201_CREATED)
def creat_item(item: schemas.SingleItem, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_item = models.Expense(
        owner_id=current_user.id, **item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    new_item_id = {'id': new_item.id}
    calculation_expenses_per_group_per_member.update_spent_amount(
        current_user.id, item.expenses_group_id, db)
    calculation_expenses_per_group_per_member.calculate_total_amount_group(
        current_user.id, item.expenses_group_id, db)
    return new_item_id


@router.get("/items")
def get_items(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), group: Optional[int] = None):
    items_searched = db.query(models.Expense).filter(
        models.Expense.owner_id == current_user.id)
    if group == None:
        items = items_searched.all()
        return items
    else:
        items = items_searched.filter(
            models.Expense.expenses_group_id == group).all()
        return items


@router.get("/items/{id}")
def get_item_by_id(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), search: Optional[str] = None):
    expenses_by_group = db.query(models.Expense).filter(
        models.Expense.owner_id == current_user.id, models.Expense.expenses_group_id == id).order_by(models.Expense.created_at.desc())
    if search == None:
        return expenses_by_group.all()
    else:
        return expenses_by_group.filter(models.Expense.name.ilike('%' + search + '%')).all()


@ router.delete("/items/{id}")
def delete_item(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    deleting_item = db.query(models.Expense).filter(
        models.Expense.id == id)
    deleting_item_filtered = deleting_item.first()
    if not deleting_item_filtered:
        return {"Sorry, no results!"}
    deleting_item_group_id = deleting_item_filtered.expenses_group_id
    deleting_item.delete(synchronize_session=False)
    db.commit()
    calculation_expenses_per_group_per_member.update_spent_amount(
        current_user.id, deleting_item_group_id, db)
    calculation_expenses_per_group_per_member.calculate_total_amount_group(
        current_user.id, deleting_item_group_id, db)
    return Response(status_code=status.HTTP_200_OK)


@ router.put("/items/{id}")
def update_item(id: int, item: dict, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    updating_item = db.query(models.Expense).filter(
        models.Expense.id == id)
    # print(item)
    updating_item.update(item)
    db.commit()
    return {"message": "success"}
