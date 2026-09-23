import json

from sqlalchemy import select, exists

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RoomMember


async def is_room_member(
    db: AsyncSession,
    room_id: int,
    user_id: int
) -> bool:

    result = await db.scalar(

        select(
            exists().where(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id
            )
        )
    )

    return bool(result)


def message_payload(
    message_id,
    room_id,
    sender_id,
    content,
    created_at
):

    if hasattr(
        created_at,
        "isoformat"
    ):

        created_at = created_at.isoformat()

    return {

        "id": str(message_id),

        "room_id": str(room_id),

        "sender_id": str(sender_id),

        "content": content,

        "created_at": created_at
    }


def encode_message(payload):

    return json.dumps(payload)


def decode_message(value):

    return json.loads(value)