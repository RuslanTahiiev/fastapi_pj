from codecs import EncodedFile
from datetime import datetime, timedelta
from typing import Optional, Set, List

from fastapi import Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, Field, EmailStr
from pydantic.networks import HttpUrl
from starlette import status
from passlib.context import CryptContext
from jose import JWTError, jwt

from security import oauth2_, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from data import fake_users_db
from customexception import CREDENTIALS_Exception


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Image(BaseModel):
    url: HttpUrl
    name: str
    
    
class Item(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = Field(
        None, title='The description of the item', max_length=155, example='Some description...'
    )
    price: float = Field(
        None, gt=0, description='The price must be > 0', example=777.77
    )
    tax: Optional[float] = None
    tags: Set[str] = set()
    # image: Optional[List[Image]] = None


class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item]
        
    
# USER #
class BaseUser(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: EmailStr
    disabled: Optional[bool] = None
    class Config:
        schema_extra = {
            'example': {
                'username': 'flower11',
                'full_name': 'Ivan Ivanenko',
                'email': 'email@mail.com',
            }
        }
    
class UserIn(BaseUser):
    password: str
    class Config:
        schema_extra = {
            'example': {
                'username': 'flower11',
                'full_name': 'Ivan Ivanenko',
                'email': 'email@mail.com',
                'password': 'StrongPassword_11',
            }
        }
    
    
class UserOut(BaseUser):
    pass


class UserInDB(BaseUser):
    hashed_password: str
# USER #


# TOKEN #
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
# TOKEN #


# fake hash
# def fake_password_hasher(raw_password: str) -> str:
#     return "fakehashed" + raw_password


# save #
# def fake_save_user(user_in: UserIn) -> UserInDB:
#     hashed_password = fake_password_hasher(user_in.password)
#     user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
#     print("User saved! ..not really")
#     return user_in_db


# async def save_show_user(user_in: UserIn) -> UserOut:
#     user_in_db = fake_save_user(user_in)
#     user_out = UserOut(**user_in_db.dict())
#     return user_out
# save #


# security get current user
# def fake_decode_token(token) -> UserInDB:
#     user = get_user(fake_users_db, token)
#     return user

# deprecated
# async def get_current_user(token: str = Depends(oauth2_)) -> UserInDB:
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail='Invalid authentication credentials.',
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user       


# TRUE authenticate #
def get_user(db, username: str) -> UserInDB:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_)) -> UserInDB:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise CREDENTIALS_Exception
        token_data = TokenData(username=username)
    except JWTError:
        raise CREDENTIALS_Exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise CREDENTIALS_Exception
    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserOut:
    c_u = UserOut(**current_user.dict())
    if c_u.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return c_u
