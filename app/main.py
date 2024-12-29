# from functools import lru_cache

from fastapi import FastAPI

# from . import config
from .routers import translate


app = FastAPI(redoc_url=None)

app.include_router(translate.router)
