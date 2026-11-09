
import secrets
import hashlib

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session as DBSession

from app.models import Session as UserSession
from app.models import User
from app.config import settings


def generate_session_token() -> str:
    """
    Generate a cryptographically secure random token.
    """

    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """
    Store only the SHA-256 digest of the token.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def create_session(
    db: DBSession,
    user_id: int
) -> str:
    """
    Create a new session and return the raw token.
    The raw token is never stored in the database.
    """

    token = generate_session_token()
    token_digest = hash_session_token(token)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    expires_at = now + timedelta(
        minutes=settings.SESSION_EXPIRE_MINUTES
    )

    new_session = UserSession(
        user_id=user_id,
        token_hash=token_digest,
        expires_at=expires_at
    )

    db.add(new_session)
    db.commit()

    return token


def get_user_from_token(
    db: DBSession,
    token: str
):
    """
    Verify the session token and return its user.
    Return None if invalid or expired.
    """

    if not isinstance(token, str) or not token:
        return None

    if len(token) > 128:
        return None

    token_digest = hash_session_token(token)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    stored_session = (
        db.query(UserSession)
        .filter(
            UserSession.token_hash == token_digest
        )
        .first()
    )

    if stored_session is None:
        return None

    if stored_session.expires_at <= now:
        db.delete(stored_session)
        db.commit()
        return None

    user = (
        db.query(User)
        .filter(User.id == stored_session.user_id)
        .first()
    )

    return user


def revoke_session(
    db: DBSession,
    token: str
) -> bool:
    """
    Revoke a session during logout.
    """

    if not isinstance(token, str) or not token:
        return False

    if len(token) > 128:
        return False

    token_digest = hash_session_token(token)

    stored_session = (
        db.query(UserSession)
        .filter(
            UserSession.token_hash == token_digest
        )
        .first()
    )

    if stored_session is None:
        return False

    db.delete(stored_session)
    db.commit()

    return True
