from redis.asyncio import Redis
from redis.exceptions import ResponseError

from app.config import settings


redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


def get_redis() -> Redis:
    return redis_client


async def close_redis():
    await redis_client.aclose()


async def ensure_stream_group():
    try:
        await redis_client.xgroup_create(
            name=settings.stream_name,
            groupname=settings.consumer_group,
            id="$",
            mkstream=True,
        )

        print(
            f"Redis consumer group created: "
            f"{settings.consumer_group}"
        )

    except ResponseError as error:

        if "BUSYGROUP" in str(error):
            print(
                f"Redis consumer group already exists: "
                f"{settings.consumer_group}"
            )
        else:
            raise