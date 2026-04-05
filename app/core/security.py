from cryptography.fernet import Fernet, InvalidToken

from app.core.config import ENCRYPTION_KEY


if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY .env dosyasında tanımlı olmalıdır.")


fernet = Fernet(ENCRYPTION_KEY.encode())


def encrypt_data(text: str | None) -> str | None:
    if text is None:
        return None

    return fernet.encrypt(text.encode()).decode()


def decrypt_data(token: str | None) -> str | None:
    if token is None:
        return None

    try:
        return fernet.decrypt(token.encode()).decode()
    except InvalidToken:
        return token
