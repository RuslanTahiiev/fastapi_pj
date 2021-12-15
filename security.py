from fastapi import Header, HTTPException


async def verify_token(x_token: str = Header(...)):
    if x_token != 'token':
        raise HTTPException(status_code=400, detail='X-Token header invalid')
    return x_token