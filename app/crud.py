from sqlalchemy.orm import Session

from . import models, schemas
from .keygen import create_random_key, create_unique_key


def get_db_url_by_key(db: Session, url_key: str) -> models.URL:
    return db.query(models.URL).filter(models.URL.key == url_key, models.URL.is_active).first()


def get_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL:
    return db.query(models.URL).filter(models.URL.secret_key == secret_key, models.URL.is_active).first()


def create_db_url(db: Session, url: schemas.URLBase) -> models.URL:
    key = create_unique_key(db)
    secret_key = f"{key}_{create_random_key(length=8)}"

    db_url = models.URL(
        target_url=url.target_url, key=key, secret_key=secret_key
    )

    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return db_url


def update_visitor_count(db: Session, db_url: schemas.URL) -> models.URL:
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url


def deactivate_url_by_secret_key(db: Session, secret_key: str) -> models.URL:
    db_url = get_db_url_by_secret_key(db, secret_key)

    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)

    return db_url
