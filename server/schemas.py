from typing import Optional

from pydantic import BaseModel


class RegisterRequest(BaseModel):
    invite_code: str
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: int
    username: str
    role: str


class TeamCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class TeamJoinRequest(BaseModel):
    join_code: str


class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_user_id: int
    join_code: str
    telegram_chat_id: Optional[str]
    telegram_bot_token: Optional[str] = None
    role: Optional[str] = None


class TelegramChatUpdate(BaseModel):
    telegram_chat_id: str | None = None
    telegram_bot_token: str | None = None


class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    hotkey: Optional[str] = None
    sound_path: Optional[str] = None
    system_sound: Optional[str] = None
    volume: Optional[int] = None


class UserSettingsResponse(BaseModel):
    theme: str
    hotkey: Optional[str] = None
    sound_path: Optional[str] = None
    system_sound: Optional[str] = None
    volume: int


class MemberResponse(BaseModel):
    user_id: int
    username: str
    role: str


class PanicRequest(BaseModel):
    team_id: int


class PanicMessage(BaseModel):
    type: str = "panic_alert"
    team_id: int
    sender_user_id: int
    sender_name: str
    event_id: str
    ts: int
