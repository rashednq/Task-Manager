from fastapi import FastAPI
from database import engine
from models import Base
from routers import users, tasks

app = FastAPI(
    title="Task Manager API",
    description="Task Management System",
    version="1.1"
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    return {"message": "Task Manager API is running "}