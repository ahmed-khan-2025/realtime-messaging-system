from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from sqlalchemy.orm import DeclarativeBase

from app.config import settings


engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True
)


SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:

    async with SessionLocal() as session:
        yield session


async def init_db():

    from app.models import (
        User,
        Room,
        RoomMember,
        Message
    )

    async with engine.begin() as connection:

        await connection.run_sync(
            Base.metadata.create_all
        )