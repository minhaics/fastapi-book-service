from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import status
from typing import Optional
from fastapi import HTTPException, Request
from .utils import decode_token

class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(AccessTokenBearer, self).__init__(auto_error= auto_error)
        
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials = await super(AccessTokenBearer, self).__call__(request)
        if credentials:
            token = credentials.credentials
            token_data = decode_token(token)
            if token_data:
                return credentials
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "This token is invalid or expired",
                        "resolution": "Please get new token",
                    },
                )
