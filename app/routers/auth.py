from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import RegisterRequest, TokenResponse
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):

    # Check whether username already exists
    existing = await db.scalar(
        select(User).where(
            User.username == data.username
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    # Create user
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
    )

    try:

        db.add(user)

        await db.commit()

        await db.refresh(user)

    except Exception:

        await db.rollback()

        raise

    # Create JWT token
    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):

    # Find user
    user = await db.scalar(
        select(User).where(
            User.username == data.username
        )
    )

    # Validate credentials
    if (
        not user
        or not verify_password(
            data.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    # Create JWT token
    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token
    )