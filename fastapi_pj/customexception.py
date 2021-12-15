from fastapi import HTTPException, status


CREDENTIALS_Exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name
    