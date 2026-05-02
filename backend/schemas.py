from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(Token):
    user: UserResponse


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse


class MatchmakingRequest(BaseModel):
    skill_offer: str = Field(min_length=2, max_length=120)
    skill_want: str = Field(min_length=2, max_length=120)


class MatchResult(BaseModel):
    user_id: int
    name: str
    skill: str
    score: int = Field(ge=0, le=100)


class MatchmakingResponse(BaseModel):
    matches: list[MatchResult]


class SkillCatalogResponse(BaseModel):
    skills: list[str]


class UserMini(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class FriendRequestCreate(BaseModel):
    receiver_id: int = Field(gt=0)


class FriendRequestAction(BaseModel):
    request_id: int = Field(gt=0)


class FriendRequestResponse(BaseModel):
    id: int
    sender: UserMini
    receiver: UserMini
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FriendResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    latest_message_preview: str | None = None
    last_message_at: datetime | None = None


class FriendsResponse(BaseModel):
    friends: list[FriendResponse]
    incoming_requests: list[FriendRequestResponse]
    outgoing_requests: list[FriendRequestResponse]


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime
    read_at: datetime | None = None
    is_mine: bool


class ConversationResponse(BaseModel):
    conversation_with: UserMini
    messages: list[MessageResponse]
