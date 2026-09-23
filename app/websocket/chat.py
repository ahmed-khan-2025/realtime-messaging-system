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

    print(
        f"[WebSocket] Connection request "
        f"room={room_id}"
    )

    token = websocket.query_params.get(
        "token"
    )

    user_id = authenticate_token(
        token or ""
    )

    if not user_id:

        print(
            "[WebSocket] Authentication failed"
        )

        await websocket.close(
            code=1008
        )

        return

    print(
        f"[WebSocket] Authenticated "
        f"user_id={user_id} "
        f"room={room_id}"
    )

    async with SessionLocal() as db:

        if not await is_room_member(
            db,
            room_id,
            user_id
        ):

            print(
                f"[WebSocket] User {user_id} "
                f"is not member of room {room_id}"
            )

            await websocket.close(
                code=1008
            )

            return

    print(
        f"[WebSocket] User {user_id} "
        f"is member of room {room_id}"
    )

    await manager.connect(
        room_id,
        websocket
    )

    print(
        f"[WebSocket] User {user_id} "
        f"connected to room {room_id}"
    )

    try:

        while True:

            data = await websocket.receive_json()

            print(
                f"[WebSocket] Received "
                f"room={room_id} "
                f"user={user_id} "
                f"data={data}"
            )

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

                print(
                    f"[WebSocket] Typing event "
                    f"published "
                    f"room={room_id} "
                    f"user={user_id}"
                )

                continue

            # ---------------------------
            # Chat message
            # ---------------------------

            if message_type != "message":

                print(
                    f"[WebSocket] Ignoring "
                    f"unknown message type: "
                    f"{message_type}"
                )

                continue

            content = str(
                data.get(
                    "content",
                    ""
                )
            ).strip()

            print(
                f"[WebSocket] Message content: "
                f"{content}"
            )

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

            print(
                f"[WebSocket] Message saved "
                f"id={message.id} "
                f"room={room_id} "
                f"user={user_id}"
            )

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

            print(
                f"[WebSocket] Payload created: "
                f"{payload}"
            )

            # ---------------------------
            # Redis Stream
            # ---------------------------

            redis_message_id = await redis_client.xadd(

                settings.stream_name,

                {
                    "payload":
                    json.dumps(payload)
                },

                maxlen=10000,

                approximate=True
            )

            print(
                f"[WebSocket] Redis XADD successful "
                f"stream={settings.stream_name} "
                f"redis_id={redis_message_id}"
            )

    except WebSocketDisconnect:

        print(
            f"[WebSocket] User {user_id} "
            f"disconnected from room {room_id}"
        )

        manager.disconnect(
            room_id,
            websocket
        )

    except Exception as error:

        print(
            f"[WebSocket] ERROR "
            f"room={room_id} "
            f"user={user_id} "
            f"error={error}"
        )

        manager.disconnect(
            room_id,
            websocket
        )

        try:

            await websocket.close()

        except Exception:

            pass