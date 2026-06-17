from fastapi import APIRouter, Depends, HTTPException, status
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse
from app.utils.auth import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _make_slug(first_name: str, last_name: str) -> str:
    base = slugify(f"{first_name}-{last_name}")[:18]
    return base or "user"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    # Check for existing email
    existing = await db.execute(select(User).where(User.email_address == body.email_address))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Generate unique slug
    base_slug = _make_slug(body.first_name, body.last_name)
    slug = base_slug
    suffix = 1
    while True:
        taken = await db.execute(select(User).where(User.slug == slug))
        if not taken.scalar_one_or_none():
            break
        slug = f"{base_slug[:16]}-{suffix}"
        suffix += 1

    user = User(
        first_name=body.first_name,
        last_name=body.last_name,
        email_address=body.email_address,
        password_hash=hash_password(body.password),
        slug=slug,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(select(User).where(User.email_address == body.email_address))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
