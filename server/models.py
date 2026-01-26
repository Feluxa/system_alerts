import datetime as dt

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from server.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(32), nullable=False, default="user")
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)


class InviteCode(Base):
    __tablename__ = "invite_codes"

    code = Column(String(64), primary_key=True)
    is_active = Column(Boolean, default=True, nullable=False)
    max_uses = Column(Integer, default=1, nullable=False)
    used_count = Column(Integer, default=0, nullable=False)
    expires_at = Column(DateTime, nullable=True)


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(String(256), nullable=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    join_code = Column(String(64), unique=True, nullable=False)
    telegram_chat_id = Column(String(64), nullable=True)
    telegram_bot_token = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)

    owner = relationship("User", foreign_keys=[owner_user_id])


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (UniqueConstraint("team_id", "user_id", name="uq_team_user"),)

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(32), nullable=False, default="user")
    joined_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    theme = Column(String(16), default="dark", nullable=False)
    hotkey = Column(String(64), nullable=True)
    sound_path = Column(String(256), nullable=True)
    system_sound = Column(String(64), nullable=True)
    volume = Column(Integer, default=70, nullable=False)


class SessionToken(Base):
    __tablename__ = "session_tokens"

    token = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow, nullable=False)
