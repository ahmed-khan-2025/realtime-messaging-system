from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from app.models import (
    Room,
    RoomMember,
    Message
)

from app.schemas import (
    RoomCreate,
    RoomResponse,
    MessageResponse
)

from app.security import get_current_user_id

from app.services import is_room_member


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)


@router.post(
    "",
    response_model=RoomResponse
)
async def create_room(

    data: RoomCreate,

    user_id: int = Depends(
        get_current_user_id
    ),

    db: AsyncSession = Depends(get_db)
):

    room = Room(

        name=data.name,

        created_by=user_id
    )

    db.add(room)

    await db.flush()

    db.add(

        RoomMember(

            room_id=room.id,

            user_id=user_id
        )
    )

    await db.commit()

    await db.refresh(room)

    return room


@router.get(
    "",
    response_model=list[RoomResponse]
)
async def list_rooms(

    user_id: int = Depends(
        get_current_user_id
    ),

    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(Room)

        .join(RoomMember)

        .where(
            RoomMember.user_id == user_id
        )
    )

    return result.scalars().all()


@router.post(
    "/{room_id}/join"
)
async def join_room(

    room_id: int,

    user_id: int = Depends(
        get_current_user_id
    ),

    db: AsyncSession = Depends(get_db)
):

    room = await db.get(
        Room,
        room_id
    )

    if not room:

        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    if not await is_room_member(
        db,
        room_id,
        user_id
    ):

        db.add(

            RoomMember(

                room_id=room_id,

                user_id=user_id
            )
        )

        await db.commit()

    return {
        "message": "Joined room"
    }


@router.get(
    "/{room_id}/messages",
    response_model=list[MessageResponse]
)
async def history(

    room_id: int,

    limit: int = 50,

    user_id: int = Depends(
        get_current_user_id
    ),

    db: AsyncSession = Depends(get_db)
):

    if not await is_room_member(
        db,
        room_id,
        user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="You are not a member of this room"
        )

    limit = max(
        1,
        min(limit, 200)
    )

    result = await db.execute(

        select(Message)

        .where(
            Message.room_id == room_id
        )

        .order_by(
            Message.created_at.desc()
        )

        .limit(limit)
    )

    messages = list(
        reversed(
            result.scalars().all()
        )
    )

    return messages