from fastapi import FastAPI

from app.config import settings
from app.routers import auth_router, health_router

app = FastAPI(title=settings.app_name)
app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
