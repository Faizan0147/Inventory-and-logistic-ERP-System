"""
FastAPI dependencies for authentication and role-based access control.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    """
    Decode the JWT and return a dict with user_id, role, supplier_id.
    Raises 401 if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try: 
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return {
            "user_id": user_id,
            "role": payload.get("role"),
            "supplier_id": payload.get("supplier_id"),
        }
    except JWTError:
        raise credentials_exception


def require_role(*allowed_roles: str):
    """
    Dependency factory: returns a dependency that checks the current user's
    role against the allowed list.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("SUPERADMIN"))])
    """

    async def _check_role(
        current_user: Annotated[dict, Depends(get_current_user)],
    ) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return _check_role
