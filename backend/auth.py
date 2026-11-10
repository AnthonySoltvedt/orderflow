from pathlib import Path
import os
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError
import jwt
from dotenv import load_dotenv

# Create a password hasher using Argon2id
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Convert a password into a secure hash."""
    return password_hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """Check whether a password matches its stored hash."""
    try:
        return password_hasher.verify(stored_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


# JWT AUTHENTICATION

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 30

if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 48:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing or too short"
    )


def create_access_token(user_id: int) -> str:
    """Create a signed JWT for a user."""

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

def verify_access_token(token: str) -> int | None:
    """Verify a JWT and return the user ID."""

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if not isinstance(user_id, str):
            return None

        if not user_id.isdecimal():
            return None

        return int(user_id)

    except InvalidTokenError:
        return None


if __name__ == "__main__":
    # Use a dummy password for testing only
    test_password = "ExamplePassword123!"

    hashed = hash_password(test_password)

    print("Password hashed:", hashed.startswith("$argon2id$"))

    print(
        "Correct password:",
        verify_password(test_password, hashed)
    )

    print(
        "Incorrect password:",
        verify_password("WrongPassword", hashed)
    )
