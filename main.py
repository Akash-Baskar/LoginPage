from ast import Str
from fastapi import Depends, FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Database Configuration
DATABASE_URL = "postgresql://postgres:root@localhost:5432/login"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define your database model
class AuthModel(Base):
    __tablename__ = "auth"
    userid = Column(String(256), primary_key=True)
    pas = Column(String(256))

Base.metadata.create_all(bind=engine)

# Pydantic model for user registration
class UserRegistration(BaseModel):
    username: str
    password: str
    repeat_password: str

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes for serving HTML pages
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("master.html", {"request": request})

@app.get("/index.html", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/error.html", response_class=HTMLResponse)
async def error(request: Request):
    return templates.TemplateResponse("error.html", {"request": request})

@app.get("/failed.html", response_class=HTMLResponse)
async def failed(request: Request):
    return templates.TemplateResponse("failed.html", {"request": request})

@app.get("/registration.html", response_class=HTMLResponse)
async def registration(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})

@app.get("/success.html", response_class=HTMLResponse)
async def success(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})
    
# ... your other routes ...

# Route for displaying the registration form
@app.get("/register", response_class=HTMLResponse)
async def display_registration_form(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})

@app.post("/submitted")
async def submit_form(
    request: Request,
    db: Session = Depends(get_db)
):
    data = await request.form()
    username  = data.get("username")
    password = data.get("password")
   
    user = db.query(AuthModel).filter(AuthModel.userid == username, AuthModel.pas == password).first()
    if user is not None:
        return templates.TemplateResponse("success.html", {"request": request})
        
    else:
        return templates.TemplateResponse("error.html", {"request": request})


# Route for user registration
@app.post("/register")
async def register_user(
    user: UserRegistration,
    db: Session = Depends(get_db)
):
    existing_user = db.query(AuthModel).filter(AuthModel.userid == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    if user.password != user.repeat_password:
        raise HTTPException(status_code=400, detail="Password and Repeat password do not match")

    new_user = AuthModel(userid=user.username, pas=user.password)
    db.add(new_user)
    db.commit()
    return {"message": "Registration successful"}
