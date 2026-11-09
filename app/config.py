
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "Nestack Secure Records API"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./nestack.db"
    )

    SESSION_EXPIRE_MINUTES = int(
        os.getenv("SESSION_EXPIRE_MINUTES", "30")
    )

    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15
    MAX_REQUEST_SIZE = 16 * 1024

    def __init__(self):
        if self.SESSION_EXPIRE_MINUTES <= 0:
            raise ValueError(
                "SESSION_EXPIRE_MINUTES must be greater than zero"
            )


settings = Settings()
