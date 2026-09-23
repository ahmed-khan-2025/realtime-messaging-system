import asyncio
import json
import socket
import uuid

from redis.exceptions import TimeoutError

from app.config import settings
from app.redis_client import get_redis, ensure_stream_group
from app.websocket.manager import manager


CONSUMER_NAME = (
    f"worker-{socket.gethostname()}-{uuid.uuid4().hex[:8]}"
)


async def process_messages():

    redis = get_redis()

    await ensure_stream_group()

    print(
        f"Redis worker started | "
        f"stream={settings.stream_name} | "
        f"group={settings.consumer_group} | "
        f"consumer={CONSUMER_NAME}"
    )

    while True:

        try:

            messages = await redis.xreadgroup(
                groupname=settings.consumer_group,
                consumername=CONSUMER_NAME,
                streams={
                    settings.stream_name: ">"
                },
                count=10,
                block=5000,
            )

            # No new messages
            if not messages:
                continue

            for stream_name, entries in messages:

                for message_id, data in entries:

                    try:

                        payload_data = data.get("payload")

                        if payload_data is None:
                            print(
                                f"Message {message_id} "
                                f"does not contain payload"
                            )
                            continue

                        payload = json.loads(
                            payload_data
                        )

                        room_id = int(
                            payload["room_id"]
                        )

                        print(
                            f"Processing message "
                            f"id={message_id} "
                            f"room={room_id}"
                        )

                        # Broadcast to WebSocket clients
                        await manager.broadcast(
                            room_id,
                            payload
                        )

                        # Acknowledge message
                        await redis.xack(
                            settings.stream_name,
                            settings.consumer_group,
                            message_id,
                        )

                        print(
                            f"Message acknowledged: "
                            f"{message_id}"
                        )

                    except Exception as message_error:

                        print(
                            f"Error processing message "
                            f"{message_id}: "
                            f"{message_error}"
                        )

        except TimeoutError:

            # Normal when Redis is waiting for new messages
            continue

        except asyncio.CancelledError:

            print(
                "Redis worker stopped."
            )

            raise

        except Exception as error:

            print(
                f"Redis worker error: "
                f"{error}"
            )

            await asyncio.sleep(2)


async def start_worker():

    task = asyncio.create_task(
        process_messages()
    )

    return task


async def stop_worker(task):

    if task is None:
        return

    print(
        "Stopping Redis worker..."
    )

    task.cancel()

    try:

        await task

    except asyncio.CancelledError:

        pass

    print(
        "Redis worker stopped successfully."
    )