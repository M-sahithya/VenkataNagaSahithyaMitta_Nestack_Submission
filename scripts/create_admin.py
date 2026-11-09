from getpass import getpass

from sqlalchemy.exc import IntegrityError

from app.database import Base, engine, SessionLocal
from app.models import User
from app.security.passwords import hash_password


def create_admin():
    Base.metadata.create_all(bind=engine)

    username = input("Enter admin username: ").strip().lower()

    if len(username) < 3:
        print("Username must contain at least 3 characters.")
        return

    password = getpass("Enter admin password (minimum 12 characters): ")
    confirm_password = getpass("Confirm admin password: ")

    if len(password) < 12:
        print("Password must contain at least 12 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    db = SessionLocal()

    try:
        existing = db.query(User).filter(
            User.username == username
        ).first()

        if existing:
            print("This username already exists.")
            return

        admin = User(
            username=username,
            password_hash=hash_password(password),
            role="admin",
            failed_login_attempts=0
        )

        db.add(admin)
        db.commit()

        print("Admin account created successfully!")

    except IntegrityError:
        db.rollback()
        print("Could not create admin account.")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()