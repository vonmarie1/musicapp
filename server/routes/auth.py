import uuid
import bcrypt
from fastapi import Depends, HTTPException
from database import get_db
from models.user import User
from schmas.usercreate import UserCreate
from fastapi import APIRouter
from sqlalchemy.orm import Session
from schmas.login import UserLogin
import jwt
router = APIRouter()

@router.post('/signup', status_code=201)
def signup_user(user: UserCreate, db: Session=Depends(get_db)):
    
       user_db = db.query(User).filter(User.email == user.email).first()
       
       if user_db:
            raise HTTPException(400, 'User taken')
       
       hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
       user_db = User(id=str(uuid.uuid4()), email = user.email, name = user.name, password = hashed_pw)

       db.add(user_db)
       db.commit()
       db.refresh(user_db)

       return user_db

@router.post('/login')
def login_user(user: UserLogin, db: Session = Depends(get_db)):
      
      user_db = db.query(User).filter(User.email == user.email).first()

      if not user_db:
            raise HTTPException(400, 'User does not exist')
      
      is_match = bcrypt.checkpw(user.password.encode(), user_db.password)

      if not is_match:
            raise HTTPException(400, 'Incorrect password')

      token = jwt.encode({'id': user_db.id}, 'password_key')
      
      return {'token': token, 'user': user_db}
      
