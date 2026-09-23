from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from app.models import User

from app.schemas import UserResponse

from app.security import get_current_user_id


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=UserResponse
)
async def me(

    user_id: int = Depends(
        get_current_user_id
    ),

    db: AsyncSession = Depends(get_db)
):

    user = await db.get(
        User,
        user_id
    )

    return user