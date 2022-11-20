from datetime import datetime, timedelta
from typing import Union
from fastapi import Depends, FastAPI, HTTPException, status,Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from schema import Schema, And, Use
import pandas as pd
import joblib
import json


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
filename = './knn_fraud_model.sav'

rep_sexe = {'Male':1,'Female':0}
rep_browser = {'Chrome': 0,'Opera':1,'Safari':2 ,'IE':4 , 'FireFox':4}
rep_source = {'SEO':0 ,'Ads':1 ,'Direct':2}

fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": "$2b$12$A5Av/o.dWdsB1X90YOcSeOTLxVm4z1qyba0k51FBAkNzKDSuc2mBC",
    },
    "bob": {
        "username": "bob",
        "hashed_password": "$2b$12$1YjZ23YdXi1jtexViElHk.h71QXhm2/GdNJ73vfTOs76XSJiT0UIi",
    },
    "clementine": {
        "username": "clementine",
        "hashed_password": "$2b$12$2xz8YYDAUYWTBA4ctwYAM.91q34Lq0utILl4AD8SXa7qQ67qfgAZO",
    }

}


class Token(BaseModel):
    access_token: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str

class HelthCheck(BaseModel):
    api_status: bool

class Result(BaseModel):
    result: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="getToken")

knn = joblib.load(filename)

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/getToken", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token}


@app.get("/helthCheck",response_model=HelthCheck)
async def helth_check():
    try :
        if len(knn.classes_)==2:
            return HelthCheck(api_status=True)
    except:
        return HelthCheck(api_status=False)
    


@app.get("/fraudCheck")
async def fraudCheck(
    purchase_value: int ,
    age: int,
    signup_time:datetime=Query(datetime.now(), description='Transaction source'),
    purchase_time:datetime=Query(datetime.now()-timedelta(days=1), description='Transaction source'),
    sex: str = Query(enum=["Male","Female"], description='Transaction source'),
    source: str = Query(enum=["SEO","Ads","Direct"], description='Transaction source'),
    browser: str =  Query(enum=["Chrome", "Opera", "Safari", "IE", "FireFox"], description='Transaction browser'),
    current_user: User = Depends(get_current_active_user)):

    schema = Schema({"purchase_value": And(Use(int),lambda x:x>0),
                      "age":And(Use(int),lambda x:x>8),
                      "signup_time" : datetime,
                      "purchase_time"  : datetime,
                      "sex":And(str,lambda x : x in ("Male","Female")),
                      "source":And(str,lambda x : x in ("SEO","Ads","Direct")),
                      "browser":And(str,lambda x : x in ("Chrome", "Opera", "Safari", "IE", "FireFox"))})
    
    data = {"purchase_value": purchase_value,
                      "age":age,
                      "signup_time" : signup_time,
                      "purchase_time"  : purchase_time,
                      "sex":sex,
                      "source":source,
                      "browser":browser}

    try:
        data = schema.validate(data)
    except :
        raise HTTPException(status_code=400, detail="Bad Request")

    data.update({"delta":int((data["purchase_time"]-data["signup_time"]).total_seconds())})
    if data["delta"]<0:
        raise HTTPException(status_code=400, detail="Bad Request")
    
    data.pop("purchase_time")
    data.pop("signup_time")

    data = pd.DataFrame.from_dict([data])

    data.browser.replace(rep_browser,inplace=True)
    data.sex.replace(rep_sexe,inplace=True)
    data.source.replace(rep_source,inplace=True)

    return bool(knn.predict(data))