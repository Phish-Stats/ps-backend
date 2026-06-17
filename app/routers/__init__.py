from app.routers.auth import router as auth_router
from app.routers.concerts import router as concerts_router
from app.routers.health import router as health_router

__all__ = ["auth_router", "concerts_router", "health_router"]
