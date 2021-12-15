from typing import Optional, Set, List

from pydantic import BaseModel, Field, EmailStr
from pydantic.networks import HttpUrl

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
    
    
class BaseUser(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: EmailStr
    
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


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db
    

def save_show_user(user_in: UserIn):
    user_in_db = fake_save_user(user_in)
    user_out = UserOut(**user_in_db.dict())
    return user_out

        
class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item]
    