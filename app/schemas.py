from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=50
    )

    password: str = Field(
        min_length=6,
        max_length=100
    )


class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"


class UserResponse(BaseModel):

    id: int
    username: str

    model_config = {
        "from_attributes": True
    }


class RoomCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100
    )


class RoomResponse(BaseModel):

    id: int
    name: str
    created_by: int

    model_config = {
        "from_attributes": True
    }


class MessageResponse(BaseModel):

    id: int
    room_id: int
    sender_id: int
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }