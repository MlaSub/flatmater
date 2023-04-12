from typing import List, Optional
from .. import models, schemas, oauth2
from fastapi import Response, status, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from ..services import membership_management, miscellaneous


router = APIRouter(prefix="/expenses-group", tags=["expenses_group"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.NewGroupOut)
def create_expenses_group(group: schemas.CreateExpensesGroup, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    new_expenses_group = models.ExpensesGroup(
        **group.dict(), owner_id=current_user.id, total_amount=0, group_members=[current_user.id])
    db.add(new_expenses_group)
    db.commit()
    db.refresh(new_expenses_group)

    new_group_relation = models.ExpensesGroupMembers(
        expenses_group_id=new_expenses_group.id, user_id=current_user.id, spent=0)
    db.add(new_group_relation)
    db.commit()
    db.refresh(new_group_relation)
    db.refresh(new_expenses_group)
    return (new_expenses_group)


@router.get("")
def get_my_expenses_group(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), search: Optional[str] = None):
    all_group_where_member_prepare = db.query(models.ExpensesGroup).join(
        models.ExpensesGroupMembers, models.ExpensesGroup.id == models.ExpensesGroupMembers.expenses_group_id, isouter=True).group_by(models.ExpensesGroup).filter(models.ExpensesGroupMembers.user_id == current_user.id).order_by(models.ExpensesGroup.created_at.desc())
    if search == None:
        all_group_where_member = all_group_where_member_prepare.all()
        return (all_group_where_member)
    else:
        all_group_where_member = all_group_where_member_prepare.filter(
            models.ExpensesGroup.title.ilike("%" + search + "%")).all()
        return (all_group_where_member)


# def object_as_dict(obj):
#     return {c.key: getattr(obj, c.key)
#             for c in inspect(obj).mapper.column_attrs}

@router.get("/{id}")
def get_one_group(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    searched_group = db.query(models.ExpensesGroup).filter(
        models.ExpensesGroup.id == id).first()
    if searched_group:
        searched_group_obj = miscellaneous.object_as_dict(searched_group)
        users_list = []
        for i in searched_group.group_members:
            one_user = db.query(models.User).filter(
                models.User.id == i).first()
            one_user_data = {
                "id": one_user.id,
                "name": one_user.name,
                "surname": one_user.surname,
                "email": one_user.email
            }
            users_list.append(one_user_data)
        searched_group_obj["users"] = users_list
        return searched_group_obj
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


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
    membership_management.add_member_to_group(
        db, item.user_id, item.expenses_group_id)
    return {"message": "success"}


@router.delete("/member/{user_id}/group/{group_id}")
def delete_member_expense_group(user_id: int, group_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    member_query = db.query(models.ExpensesGroupMembers).filter(models.ExpensesGroupMembers.user_id ==
                                                                user_id, models.ExpensesGroupMembers.expenses_group_id == group_id)
    member_query.delete(synchronize_session=False)
    db.commit()
    membership_management.removing_member_from_group(db, user_id, group_id)
    return Response(status_code=status.HTTP_200_OK)
