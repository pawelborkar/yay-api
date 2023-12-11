import string
import secrets

from sqlalchemy.orm import Session
from . import crud


def create_random_key(length: int = 5) -> str:
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    random_key = "".join(secrets.choice(chars) for _ in range(length))
    return random_key


def create_unique_key(db: Session) -> str:
    key = create_random_key()

    while crud.get_db_url_by_key(db, key):
        key = create_random_key()
    return key
