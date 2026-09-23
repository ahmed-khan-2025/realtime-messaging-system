from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.database import get_db

from app.models import (
    Room,
    RoomMember,
)

from app.schemas import (
    RoomCreate,
    RoomResponse,
)

from app.security import (
    get_current_user_id,
)


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
)


# ============================================================
# CREATE ROOM
# ============================================================

@router.post(
    "",
    response_model=RoomResponse,
)
async def create_room(
    data: RoomCreate,

    db: AsyncSession = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),
):

    # --------------------------------------------------------
    # Create room
    # --------------------------------------------------------

    room = Room(
        name=data.name,
        created_by=user_id,
    )

    db.add(room)

    # --------------------------------------------------------
    # Flush so PostgreSQL generates room.id
    # --------------------------------------------------------

    await db.flush()

    # --------------------------------------------------------
    # Automatically make creator a room member
    # --------------------------------------------------------

    member = RoomMember(
        room_id=room.id,
        user_id=user_id,
    )

    db.add(member)

    # --------------------------------------------------------
    # Save everything
    # --------------------------------------------------------

    await db.commit()

    await db.refresh(room)

    return room


# ============================================================
# LIST ROOMS
# ============================================================

@router.get(
    "",
    response_model=list[RoomResponse],
)
async def list_rooms(
    db: AsyncSession = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),
):

    result = await db.execute(
        select(Room)
        .order_by(
            Room.id
        )
    )

    rooms = result.scalars().all()

    return rooms


# ============================================================
# JOIN ROOM
# ============================================================

@router.post(
    "/{room_id}/join",
)
async def join_room(
    room_id: int,

    db: AsyncSession = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),
):

    # --------------------------------------------------------
    # Check room
    # --------------------------------------------------------

    room = await db.scalar(
        select(Room).where(
            Room.id == room_id
        )
    )

    if not room:

        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    # --------------------------------------------------------
    # Check existing membership
    # --------------------------------------------------------

    existing_member = await db.scalar(
        select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id,
        )
    )

    if existing_member:

        return {
            "message": "Already a member of the room",

            "room_id": room_id,

            "user_id": user_id,
        }

    # --------------------------------------------------------
    # Add member
    # --------------------------------------------------------

    member = RoomMember(
        room_id=room_id,
        user_id=user_id,
    )

    db.add(member)

    await db.commit()

    return {
        "message": "Joined room successfully",

        "room_id": room_id,

        "user_id": user_id,
    }


# ============================================================
# GET ROOM MESSAGES
# ============================================================

@router.get(
    "/{room_id}/messages",
)
async def get_room_messages(
    room_id: int,

    db: AsyncSession = Depends(
        get_db
    ),

    user_id: int = Depends(
        get_current_user_id
    ),
):

    # --------------------------------------------------------
    # Check room
    # --------------------------------------------------------

    room = await db.scalar(
        select(Room).where(
            Room.id == room_id
        )
    )

    if not room:

        raise HTTPException(
            status_code=404,
            detail="Room not found",
        )

    # --------------------------------------------------------
    # Check membership
    # --------------------------------------------------------

    member = await db.scalar(
        select(RoomMember).where(
            RoomMember.room_id == room_id,
            RoomMember.user_id == user_id,
        )
    )

    if not member:

        raise HTTPException(
            status_code=403,
            detail="You are not a member of this room",
        )

    # --------------------------------------------------------
    # Load messages
    # --------------------------------------------------------

    from app.models import Message

    result = await db.execute(
        select(Message)
        .where(
            Message.room_id == room_id
        )
        .order_by(
            Message.created_at
        )
    )

    messages = result.scalars().all()

    return messages