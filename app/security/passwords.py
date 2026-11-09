
from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError
)

# Argon2id password hashing configuration
password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16
)


def hash_password(password: str) -> str:
    """
    Generate a secure Argon2id password hash.
    Argon2 automatically generates a unique salt.
    """

    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    if not password:
        raise ValueError("Password cannot be empty")

    return password_hasher.hash(password)


def verify_password(
    password: str,
    stored_hash: str
) -> bool:
    """
    Verify a password against its stored Argon2id hash.
    """

    if not isinstance(password, str):
        return False

    if not isinstance(stored_hash, str):
        return False

    try:
        return password_hasher.verify(
            stored_hash,
            password
        )

    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError
    ):
        return False


def needs_rehash(stored_hash: str) -> bool:
    """
    Check whether an existing password hash
    needs stronger hashing parameters.
    """

    try:
        return password_hasher.check_needs_rehash(
            stored_hash
        )
    except (VerificationError, InvalidHashError):
        return True
