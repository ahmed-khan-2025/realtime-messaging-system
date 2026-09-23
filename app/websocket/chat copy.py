import json

from datetime import (
    datetime,
    timezone
)

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from jose import (
    jwt,
    JWTError
)

from app.config import settings

from app.database import SessionLocal

from app.models import Message

from app.redis_client import redis_client

from app.services import (
    is_room_member,
    message_payload
)

from app.websocket.manager import manager


router = APIRouter()


def authenticate_token(
    token: str
) -> int | None:

    try:

        payload = jwt.decode(

            token,

            settings.jwt_secret,

            algorithms=[
                settings.jwt_algorithm
            ]
        )

        return int(
            payload["sub"]
        )

    except (
        JWTError,
        KeyError,
        ValueError
    ):

        return None


@router.websocket(
    "/ws/rooms/{room_id}"
)
async def websocket_chat(

    websocket: WebSocket,

    room_id: int
):

    token = websocket.query_params.get(
        "token"
    )

    user_id = authenticate_token(
        token or ""
    )

    if not user_id:

        await websocket.close(
            code=1008
        )

        return

    async with SessionLocal() as db:

        if not await is_room_member(
            db,
            room_id,
            user_id
        ):

            await websocket.close(
                code=1008
            )

            return

    await manager.connect(
        room_id,
        websocket
    )

    try:

        while True:

            data = await websocket.receive_json()

            message_type = data.get(
                "type",
                "message"
            )

            # ---------------------------
            # Typing indicator
            # ---------------------------

            if message_type == "typing":

                await redis_client.publish(

                    f"room:{room_id}:typing",

                    json.dumps({

                        "user_id": user_id,

                        "typing": bool(
                            data.get(
                                "typing",
                                True
                            )
                        )
                    })
                )

                continue

            # ---------------------------
            # Chat message
            # ---------------------------

            if message_type != "message":

                continue

            content = str(
                data.get(
                    "content",
                    ""
                )
            ).strip()

            if (
                not content
                or
                len(content) > 2000
            ):

                await websocket.send_json({

                    "type": "error",

                    "message":
                    "Message must be 1-2000 characters"
                })

                continue

            # ---------------------------
            # Save message
            # ---------------------------

            async with SessionLocal() as db:

                message = Message(

                    room_id=room_id,

                    sender_id=user_id,

                    content=content,

                    created_at=datetime.now(
                        timezone.utc
                    )
                )

                db.add(message)

                await db.commit()

                await db.refresh(message)

            # ---------------------------
            # Create event
            # ---------------------------

            payload = message_payload(

                message.id,

                room_id,

                user_id,

                content,

                message.created_at
            )

            # ---------------------------
            # Redis Stream
            # ---------------------------

            await redis_client.xadd(

                settings.stream_name,

                {
                    "payload":
                    json.dumps(payload)
                },

                maxlen=10000,

                approximate=True
            )

    except WebSocketDisconnect:

        manager.disconnect(
            room_id,
            websocket
        )

    except Exception:

        manager.disconnect(
            room_id,
            websocket
        )

        try:

            await websocket.close()

        except Exception:

            pass