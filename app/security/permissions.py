from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.sessions import get_user_from_token
from app.models import User


bearer_scheme = HTTPBearer(
    scheme_name="Bearer Authentication",
    auto_error=False
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    token = credentials.credentials

    user = get_user_from_token(db, token)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token"
        )

    return user


def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user


def verify_record_access(
    record_owner_id: int,
    current_user: User
) -> bool:

    if current_user.role == "admin":
        return True

    return record_owner_id == current_user.id