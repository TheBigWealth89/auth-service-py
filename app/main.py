from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define a Pydantic model (like Zod schema)
class User(BaseModel):
    username: str
    email: str

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI 👋"}

@app.post("/register")
def register_user(user: User):
    return {"user": user}