from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=255)
    new_password: str = Field(min_length=6, max_length=128)


class RequestEmailVerification(BaseModel):
    email: EmailStr


class ConfirmEmailVerification(BaseModel):
    token: str = Field(min_length=20, max_length=255)


class MessageEnvelope(BaseModel):
    message: str
    token: str | None = None


class SocialLinksResponse(BaseModel):
    linkedin: str = ""
    website: str = ""
    x: str = ""


class SkillResponse(BaseModel):
    id: int
    name: str
    slug: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    bio: str = ""
    city: str = ""
    availability: str = ""
    experience_level: str = "intermediate"
    rating_average: float = 0
    rating_count: int = 0
    avatar_url: str | None = None
    social_links: SocialLinksResponse
    skills_offered: list[SkillResponse] = []
    skills_wanted: list[SkillResponse] = []


class UserMini(BaseModel):
    id: int
    name: str
    email: EmailStr
    avatar_url: str | None = None
    city: str | None = None
    rating_average: float = 0

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_verified: bool
    is_admin: bool = False
    profile: ProfileResponse
    followers_count: int = 0
    following_count: int = 0
    friends_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(Token):
    user: UserResponse


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse


class UpdateProfileRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    bio: str = Field(default="", max_length=2000)
    city: str = Field(default="", max_length=120)
    availability: str = Field(default="", max_length=500)
    experience_level: str = Field(default="intermediate", max_length=40)
    linkedin: str = Field(default="", max_length=255)
    website: str = Field(default="", max_length=255)
    x: str = Field(default="", max_length=255)
    skills_offered: list[str] = Field(default_factory=list, max_length=20)
    skills_wanted: list[str] = Field(default_factory=list, max_length=20)


class ProfileMetrics(BaseModel):
    credibility: str
    discoverability: str
    conversation_fit: str


class MatchmakingRequest(BaseModel):
    skill_offer: str = Field(min_length=2, max_length=120)
    skill_want: str = Field(min_length=2, max_length=120)


class MatchResult(BaseModel):
    user_id: int
    name: str
    skill: str
    score: int = Field(ge=0, le=100)
    city: str | None = None
    rating_average: float = 0
    shared_skills: list[str] = []


class MatchmakingResponse(BaseModel):
    matches: list[MatchResult]


class SkillCatalogResponse(BaseModel):
    skills: list[str]


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


class FriendResponse(UserMini):
    latest_message_preview: str | None = None
    last_message_at: datetime | None = None
    is_online: bool = False


class FriendsResponse(BaseModel):
    friends: list[FriendResponse]
    incoming_requests: list[FriendRequestResponse]
    outgoing_requests: list[FriendRequestResponse]
    followers: list[UserMini] = []
    following: list[UserMini] = []


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    is_mine: bool
    message_type: str = "text"
    attachment_url: str | None = None
    attachment_filename: str | None = None


class ConversationResponse(BaseModel):
    conversation_with: UserMini
    messages: list[MessageResponse]


class TypingEvent(BaseModel):
    recipient_id: int = Field(gt=0)
    is_typing: bool = True


class ReadReceiptEvent(BaseModel):
    recipient_id: int = Field(gt=0)


class FollowResponse(BaseModel):
    following: bool
    user_id: int


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    body: str
    link_url: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardStat(BaseModel):
    label: str
    value: str
    delta: str


class DashboardActivityItem(BaseModel):
    title: str
    body: str
    time: str


class DashboardSessionItem(BaseModel):
    title: str
    time: str
    tone: str = "from-slate-100 to-white"


class DashboardSkillItem(BaseModel):
    label: str
    value: int = Field(ge=0, le=100)
    note: str


class DashboardSummaryResponse(BaseModel):
    stats: list[DashboardStat]
    activity: list[DashboardActivityItem]
    suggested_matches: list[MatchResult]
    upcoming: list[DashboardSessionItem]
    skills: list[DashboardSkillItem]
    notifications: list[NotificationResponse]
    pending_requests: int
    unread_messages: int


class ReviewCreate(BaseModel):
    reviewee_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=1500)
    endorsement: str = Field(default="", max_length=160)


class ReviewResponse(BaseModel):
    id: int
    reviewer: UserMini
    reviewee_id: int
    rating: int
    comment: str
    endorsement: str
    created_at: datetime


class LearningRequestCreate(BaseModel):
    skill: str = Field(min_length=2, max_length=120)
    title: str = Field(min_length=4, max_length=160)
    description: str = Field(min_length=12, max_length=3000)
    city: str = Field(default="", max_length=120)
    availability: str = Field(default="", max_length=500)


class LearningRequestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=4, max_length=160)
    description: str | None = Field(default=None, min_length=12, max_length=3000)
    city: str | None = Field(default=None, max_length=120)
    availability: str | None = Field(default=None, max_length=500)
    status: str | None = Field(default=None, max_length=20)


class LearningRequestApplicationCreate(BaseModel):
    message: str = Field(default="", max_length=2000)


class LearningRequestApplicationResponse(BaseModel):
    id: int
    applicant: UserMini
    status: str
    message: str
    created_at: datetime


class LearningRequestResponse(BaseModel):
    id: int
    title: str
    description: str
    city: str
    availability: str
    status: str
    created_at: datetime
    updated_at: datetime
    creator: UserMini
    skill: SkillResponse
    applications_count: int
    applications: list[LearningRequestApplicationResponse] = []


class PaginatedLearningRequestsResponse(BaseModel):
    items: list[LearningRequestResponse]
    total: int
    page: int
    page_size: int


class AdminUserUpdate(BaseModel):
    is_admin: bool | None = None
    is_verified: bool | None = None


class AdminSummaryResponse(BaseModel):
    total_users: int
    verified_users: int
    open_learning_requests: int
    pending_friend_requests: int
    total_messages: int


class DiscoverUsersResponse(BaseModel):
    items: list[UserMini]
    total: int
    page: int
    page_size: int
