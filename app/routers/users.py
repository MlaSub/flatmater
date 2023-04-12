from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from ..services import miscellaneous, membership_management

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    new_password = utils.hash(user.password)
    user.password = new_password
    new_user = models.User(**user.dict())
    check_user = db.query(models.User).filter(
        models.User.email == user.email).first()
    if not check_user:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@router.get("/all", response_model=List[schemas.UserOut])
def get_all_other_user(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), search: Optional[str] = None, group: Optional[int] = None):
    all_other_users = db.query(models.User).filter(
        models.User.id != current_user.id)
    if search == None:
        all_other_users = all_other_users.all()
    else:
        all_other_users = all_other_users.filter((
            models.User.name + ' ' + models.User.surname).ilike('%' + search + '%')).all()
    list_of_users = []
    if group != None:
        for user in all_other_users:
            all_other_users_one = miscellaneous.object_as_dict(user)
            all_other_users_one["member"] = membership_management.member_of_group(
                db, user.id, group)
            list_of_users.append(all_other_users_one)
        return list_of_users
    else:
        return all_other_users


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user_new = db.query(models.User).filter(models.User.id == id)
    user = user_new.first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    else:
        # return (user)
        return {"message": "success"}
