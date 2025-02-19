import logging
import uuid
from fastapi import HTTPException
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from src.config import Config
from typing import Optional
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired, BadSignature

passwd_context = CryptContext(schemes=["bcrypt"])

def generate_password_hash(password: str) -> str:
    hash = passwd_context.hash(password)
    return hash

def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)

def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
) -> str:
    payload = {
        "user": user_data,
        "exp": datetime.now()
        + (expiry if expiry is not None else timedelta(minutes=60)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    
    token = jwt.encode(
        payload=payload, 
        key= Config.JWT_SECRET, 
        algorithm=Config.JWT_ALGORITHM
    )
    return token

def decode_token(token: str) -> Optional[dict]:
    try:
        token_data = jwt.decode(
            jwt=token,
            algorithms=[Config.JWT_ALGORITHM],
            key=Config.JWT_SECRET,
        )
        return token_data

    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None

    except Exception as e:
        logging.exception(e)
        return None

serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="email-configuration"
)

def create_url_safe_token(data: dict) -> str:
    """
    Create a URL-safe token with an expiration time.
    """
    return serializer.dumps(data)


def decode_url_safe_token(token: str, max_age=3600) -> dict:
    """
    Decode a URL-safe token and check for expiration.
    """
    try:
        # Deserialize the token and check if it's expired
        data = serializer.loads(token, max_age=max_age)
        return data
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Token has expired")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    
