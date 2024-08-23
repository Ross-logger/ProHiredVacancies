import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.config import JWT_SECRET

ALGORITHM = "HS256"


def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
        print("PAYLOAD:", payload)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Invalid token")
        return int(user_id)

    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))


