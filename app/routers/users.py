from sqlalchemy.orm import Session
from ..database import get_db
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils

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


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user_new = db.query(models.User).filter(models.User.id == id)
    user = user_new.first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    else:
        # return (user)
        return {"message": "success"}
