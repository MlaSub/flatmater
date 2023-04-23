from fastapi import FastAPI
from . import models
from .database import engine
from .routers import expenses_group, users, auth, expenses, overview
from fastapi.middleware.cors import CORSMiddleware
from .services.modules.user_debt import single_membership_debt_per_member

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.include_router(calculation_expenses_per_group_per_member.router)
app.include_router(expenses.router)
app.include_router(expenses_group.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(overview.router)
# app.include_router(single_membership_debt_per_member.router)
