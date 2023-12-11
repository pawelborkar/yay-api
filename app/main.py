import time
import httpx
import validators

import asyncio

from starlette.datastructures import URL
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from . import models, schemas
from .config import get_settings

from .database import SessionLocal, engine
from .crud import create_db_url, deactivate_url_by_secret_key, get_db_url_by_key, get_db_url_by_secret_key, update_visitor_count

app = FastAPI(title="YAY", description="YAY: URL Shortener, Visit: https://yay.pawel.in",
              url='https://yay.pawel.in')

origins = get_settings().origins
print(get_settings().env_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

tags_metadata = [
    {"name": "user", "description": "Operations related to user"},
    {"name": "admin", "description": "Admin Operations."}
]


models.Base.metadata.create_all(bind=engine)


async def ping_url(url):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            print(f"Ping successful at {time.ctime()} to URL: {get_settings().base_url}")
        except httpx.Request:
            print(f"Error: {e}")


async def background_ping():
    url_to_ping = get_settings().base_url

    while True:
        await ping_url(url_to_ping)
        # Sleep for 14 minutes and 50 seconds
        await asyncio.sleep(14 * 60 + 50)


@app.on_event("startup")
async def startup_event():
    # Start the background ping coroutine when the server starts
    asyncio.create_task(background_ping())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_admin_info(db_url: models.URL) -> schemas.URLInformation:
    base_url = URL(get_settings().base_url)
    admin_endpoint = app.url_path_for(
        "administration information", secret_key=db_url.secret_key)
    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))

    return db_url


def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exists."
    raise HTTPException(status_code=404, detail=message)


def raise_bad_request(message: str):
    raise HTTPException(status_code=400, detail=message)


@app.get("/", tags=["User"])
def home():
    return RedirectResponse(get_settings().base_url + '/docs')


@app.get("/{url_key}", tags=["User"])
def forward_to_target_url(
    url_key: str,
    request: Request,
    db: Session = Depends(get_db)
):
    if db_url := get_db_url_by_key(db=db, url_key=url_key):
        update_visitor_count(db=db, db_url=db_url)
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)


@app.post("/url", response_model=schemas.URLInformation, tags=["User"])
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_request(message="Invalid URL. Please update and try again")

    db_url = create_db_url(db=db, url=url)
    return get_admin_info(db_url)


@app.get("/admin/{secret_key}", name="administration information", response_model=schemas.URLInformation, tags=["Admin"])
def get_url_info(secret_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := get_db_url_by_secret_key(db=db, secret_key=secret_key):
        return get_admin_info(db_url)
    else:
        raise_not_found(request)


@app.delete("/admin/{secret_key}",  tags=["Admin"])
def deactivate_url(secret_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := deactivate_url_by_secret_key(db=db, secret_key=secret_key):
        message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)
