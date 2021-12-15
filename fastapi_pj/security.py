from fastapi import Header, HTTPException
from fastapi.security import OAuth2PasswordBearer, oauth2

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def verify_token(x_token: str = Header(...)):
    if x_token != 'token':
        raise HTTPException(status_code=400, detail='X-Token header invalid')
    return x_token


oauth2_ = OAuth2PasswordBearer(tokenUrl='token')
