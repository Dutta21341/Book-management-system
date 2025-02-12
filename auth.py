from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)):
    if token != "fake-jwt-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": "user"}
