
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User
from app.schemas import RegisterRequest, LoginRequest
from app.security.passwords import hash_password, verify_password
from app.security.sessions import create_session, revoke_session
from app.security.permissions import get_current_user
from app.models import User as UserModel

router = APIRouter()


@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    username = data.username.strip().lower()

    existing_user = db.query(User).filter(
        User.username == username
    ).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    user = User(
        username=username,
        password_hash=hash_password(data.password),
        role="user",
        failed_login_attempts=0
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username already exists")

    return {
        "message": "Registration successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    username = data.username.strip().lower()

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if user.locked_until and user.locked_until > now:
        raise HTTPException(
            status_code=429,
            detail="Account temporarily locked. Try again later."
        )

    if user.locked_until and user.locked_until <= now:
        user.failed_login_attempts = 0
        user.locked_until = None

    if not verify_password(data.password, user.password_hash):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= 5:
            user.locked_until = now + timedelta(minutes=15)
            db.commit()
            raise HTTPException(
                status_code=429,
                detail="Account temporarily locked. Try again later."
            )

        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    token = create_session(db, user.id)

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "expires_in_minutes": 30
    }


@router.post("/logout")
def logout(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    credentials = Depends(__import__("fastapi").security.HTTPBearer())
):
    revoke_session(db, credentials.credentials)

    return {"message": "Logout successful"}
