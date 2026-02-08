import os
import time
import uuid
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from server.auth import hash_password, issue_token, verify_password
from server.db import Base, engine, get_db
from server.models import AppConfig, InviteCode, SessionToken, Team, TeamMember, User, UserSettings
from server.schemas import (
    AuthResponse,
    LoginRequest,
    PanicMessage,
    PanicRequest,
    RegisterRequest,
    TeamCreateRequest,
    TeamJoinRequest,
    TeamResponse,
    MemberResponse,
    TeamUpdateRequest,
    TelegramChatUpdate,
    UserSettingsResponse,
    UserSettingsUpdate,
    VersionInfoResponse,
    VersionPolicyUpdateRequest,
)
from server.telegram import format_alert, send_telegram_message
from server.ws import ConnectionManager


app = FastAPI(title="Alerts Backend")
manager = ConnectionManager()

Base.metadata.create_all(bind=engine)

COOLDOWN_USER_SEC = 1
COOLDOWN_TEAM_SEC = 1
_user_last = {}
_team_last = {}
MIN_CLIENT_VERSION = os.getenv("MIN_CLIENT_VERSION", "1.0.0")
LATEST_CLIENT_VERSION = os.getenv("LATEST_CLIENT_VERSION", MIN_CLIENT_VERSION)
CLIENT_DOWNLOAD_URL = os.getenv("CLIENT_DOWNLOAD_URL", "https://github.com/Feluxa/system_alerts/releases")
CLIENT_HARD_BLOCK = os.getenv("CLIENT_HARD_BLOCK", "true").strip().lower() not in ("0", "false", "off", "no")
CFG_MIN_CLIENT_VERSION = "min_client_version"
CFG_LATEST_CLIENT_VERSION = "latest_client_version"
CFG_CLIENT_DOWNLOAD_URL = "client_download_url"
CFG_CLIENT_HARD_BLOCK = "client_hard_block"


def _team_members_payload(db: Session, team_id: int):
    rows = (
        db.query(User, TeamMember)
        .join(TeamMember, TeamMember.user_id == User.id)
        .filter(TeamMember.team_id == team_id)
        .all()
    )
    members = []
    for u, tm in rows:
        members.append({"user_id": u.id, "username": u.username, "role": tm.role})
    return members


def _require_super_admin(user: User):
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Forbidden")


def _upsert_config(db: Session, key: str, value: str):
    row = db.get(AppConfig, key)
    if row:
        row.value = value
    else:
        db.add(AppConfig(key=key, value=value))


def _bool_to_str(value: bool) -> str:
    return "true" if value else "false"


def _str_to_bool(value: str, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "on", "yes")


def _version_policy(db: Session) -> dict:
    rows = db.query(AppConfig).filter(
        AppConfig.key.in_(
            [CFG_MIN_CLIENT_VERSION, CFG_LATEST_CLIENT_VERSION, CFG_CLIENT_DOWNLOAD_URL, CFG_CLIENT_HARD_BLOCK]
        )
    ).all()
    data = {row.key: row.value for row in rows}
    min_client = data.get(CFG_MIN_CLIENT_VERSION, MIN_CLIENT_VERSION)
    latest_client = data.get(CFG_LATEST_CLIENT_VERSION, LATEST_CLIENT_VERSION)
    return {
        "min_client_version": min_client,
        "latest_client_version": latest_client,
        "download_url": data.get(CFG_CLIENT_DOWNLOAD_URL, CLIENT_DOWNLOAD_URL),
        "hard_block": _str_to_bool(data.get(CFG_CLIENT_HARD_BLOCK), CLIENT_HARD_BLOCK),
    }


@app.on_event("startup")
def _bootstrap_invite():
    from server.db import SessionLocal
    from sqlalchemy import text

    db = SessionLocal()
    try:
        if db.query(User).count() == 0 and db.query(InviteCode).count() == 0:
            db.add(InviteCode(code="BOOTSTRAP", is_active=True, max_uses=1, used_count=0))
            db.commit()
        # Seed runtime-editable version policy (can be changed from admin panel).
        if not db.get(AppConfig, CFG_MIN_CLIENT_VERSION):
            _upsert_config(db, CFG_MIN_CLIENT_VERSION, MIN_CLIENT_VERSION)
            _upsert_config(db, CFG_LATEST_CLIENT_VERSION, LATEST_CLIENT_VERSION)
            _upsert_config(db, CFG_CLIENT_DOWNLOAD_URL, CLIENT_DOWNLOAD_URL)
            _upsert_config(db, CFG_CLIENT_HARD_BLOCK, _bool_to_str(CLIENT_HARD_BLOCK))
            db.commit()
        if engine.url.drivername.startswith("sqlite"):
            from sqlalchemy import text
            cols = [row[1] for row in db.execute(text("PRAGMA table_info(teams)")).fetchall()]
            if "telegram_bot_token" not in cols:
                db.execute(text("ALTER TABLE teams ADD COLUMN telegram_bot_token VARCHAR(128)"))
                db.commit()
    finally:
        db.close()


def _get_user_by_token(db: Session, token: str) -> Optional[User]:
    session = db.get(SessionToken, token)
    if not session:
        return None
    return db.get(User, session.user_id)


def _extract_token(auth_header: str | None, token: str | None) -> Optional[str]:
    if token:
        return token
    if not auth_header:
        return None
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1]
    return auth_header


def _require_token(token: str | None, auth_header: str | None, db: Session) -> User:
    token = _extract_token(auth_header, token)
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    user = _get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@app.post("/auth/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    invite = db.get(InviteCode, payload.invite_code)
    if not invite or not invite.is_active:
        raise HTTPException(status_code=400, detail="Invalid invite code")
    if invite.expires_at and invite.expires_at.timestamp() < time.time():
        raise HTTPException(status_code=400, detail="Invite expired")
    if invite.used_count >= invite.max_uses:
        raise HTTPException(status_code=400, detail="Invite exhausted")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username taken")

    role = "super_admin" if db.query(User).count() == 0 else "user"
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=role,
    )
    db.add(user)
    db.flush()
    settings = UserSettings(user_id=user.id, volume=70)
    db.add(settings)
    invite.used_count += 1
    if invite.used_count >= invite.max_uses:
        invite.is_active = False
    token = issue_token()
    db.add(SessionToken(token=token, user_id=user.id))
    db.commit()
    return AuthResponse(token=token, user_id=user.id, username=user.username, role=user.role)


@app.get("/meta/version", response_model=VersionInfoResponse)
def meta_version(db: Session = Depends(get_db)):
    return VersionInfoResponse(**_version_policy(db))


@app.get("/admin/version-policy", response_model=VersionInfoResponse)
def admin_get_version_policy(
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    _require_super_admin(user)
    return VersionInfoResponse(**_version_policy(db))


@app.patch("/admin/version-policy", response_model=VersionInfoResponse)
def admin_update_version_policy(
    payload: VersionPolicyUpdateRequest,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    _require_super_admin(user)
    current = _version_policy(db)
    if payload.min_client_version is not None:
        _upsert_config(db, CFG_MIN_CLIENT_VERSION, payload.min_client_version.strip())
    if payload.latest_client_version is not None:
        _upsert_config(db, CFG_LATEST_CLIENT_VERSION, payload.latest_client_version.strip())
    if payload.download_url is not None:
        _upsert_config(db, CFG_CLIENT_DOWNLOAD_URL, payload.download_url.strip())
    if payload.hard_block is not None:
        _upsert_config(db, CFG_CLIENT_HARD_BLOCK, _bool_to_str(payload.hard_block))
    db.commit()
    # Ensure latest >= min if admin only changed one field.
    updated = _version_policy(db)
    if not updated["latest_client_version"]:
        _upsert_config(db, CFG_LATEST_CLIENT_VERSION, updated["min_client_version"])
        db.commit()
        updated = _version_policy(db)
    return VersionInfoResponse(**{**current, **updated})


@app.post("/invites/create")
def create_invite(
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    code = f"INV-{uuid.uuid4().hex[:8]}"
    invite = InviteCode(code=code, is_active=True, max_uses=1, used_count=0)
    db.add(invite)
    db.commit()
    return {"code": code}


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        print(f"[AUTH] login failed for {payload.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = issue_token()
    db.add(SessionToken(token=token, user_id=user.id))
    db.commit()
    print(f"[AUTH] login ok for {payload.username}")
    return AuthResponse(token=token, user_id=user.id, username=user.username, role=user.role)


@app.post("/teams/create", response_model=TeamResponse)
def create_team(
    payload: TeamCreateRequest,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    existing = db.query(TeamMember).filter(TeamMember.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already in a team")
    join_code = f"TEAM-{uuid.uuid4().hex[:8]}"
    team = Team(
        name=payload.name,
        description=payload.description,
        owner_user_id=user.id,
        join_code=join_code,
    )
    db.add(team)
    db.flush()
    db.add(TeamMember(team_id=team.id, user_id=user.id, role="owner"))
    db.commit()
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        owner_user_id=team.owner_user_id,
        join_code=team.join_code,
        telegram_chat_id=team.telegram_chat_id,
        role="owner",
    )


@app.post("/teams/join", response_model=TeamResponse)
async def join_team(
    payload: TeamJoinRequest,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    existing = db.query(TeamMember).filter(TeamMember.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already in a team")
    team = db.query(Team).filter(Team.join_code == payload.join_code).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.add(TeamMember(team_id=team.id, user_id=user.id, role="user"))
    db.commit()
    members = _team_members_payload(db, team.id)
    print("[WS] team_update join:", team.id)
    await manager.broadcast(team.id, {"type": "team_update", "team_id": team.id, "members": members})
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        owner_user_id=team.owner_user_id,
        join_code=team.join_code,
        telegram_chat_id=team.telegram_chat_id,
        role="user",
    )


@app.get("/teams/my", response_model=Optional[TeamResponse])
def my_team(
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    membership = db.query(TeamMember).filter(TeamMember.user_id == user.id).first()
    if not membership:
        return None
    team = db.get(Team, membership.team_id)
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        owner_user_id=team.owner_user_id,
        join_code=team.join_code,
        telegram_chat_id=team.telegram_chat_id,
        role=membership.role,
    )


@app.patch("/teams/{team_id}/telegram_chat", response_model=TeamResponse)
def set_telegram_chat(
    team_id: int,
    payload: TelegramChatUpdate,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id, TeamMember.team_id == team_id
    ).first()
    if not membership and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not in team")
    if membership and membership.role not in ("owner", "admin") and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if payload.telegram_chat_id is not None:
        team.telegram_chat_id = payload.telegram_chat_id
    if payload.telegram_bot_token is not None:
        team.telegram_bot_token = payload.telegram_bot_token
    db.commit()
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        owner_user_id=team.owner_user_id,
        join_code=team.join_code,
        telegram_chat_id=team.telegram_chat_id,
        role=membership.role if membership else None,
    )


@app.patch("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    payload: TeamUpdateRequest,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id, TeamMember.team_id == team_id
    ).first()
    if not membership and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not in team")
    if membership and membership.role not in ("owner", "admin") and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if payload.name is not None:
        team.name = payload.name
    if payload.description is not None:
        team.description = payload.description
    db.commit()
    members = _team_members_payload(db, team_id)
    await manager.broadcast(
        team.id,
        {
            "type": "team_update",
            "team_id": team.id,
            "team": {"name": team.name, "description": team.description},
            "members": members,
        },
    )
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        owner_user_id=team.owner_user_id,
        join_code=team.join_code,
        telegram_chat_id=team.telegram_chat_id,
        role=membership.role if membership else None,
    )


@app.get("/users/settings", response_model=UserSettingsResponse)
def get_settings(
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    settings = db.get(UserSettings, user.id)
    if not settings:
        settings = UserSettings(user_id=user.id, volume=70, theme="dark")
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return UserSettingsResponse(
        theme=settings.theme or "dark",
        hotkey=settings.hotkey,
        sound_path=settings.sound_path,
        system_sound=settings.system_sound,
        volume=settings.volume,
    )


@app.patch("/users/settings")
def update_settings(
    payload: UserSettingsUpdate,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    settings = db.get(UserSettings, user.id)
    if not settings:
        settings = UserSettings(user_id=user.id, theme="dark")
        db.add(settings)
    if payload.theme is not None:
        settings.theme = payload.theme
    if payload.hotkey is not None:
        settings.hotkey = payload.hotkey
    if payload.sound_path is not None:
        settings.sound_path = payload.sound_path
    if payload.system_sound is not None:
        settings.system_sound = payload.system_sound
    if payload.volume is not None:
        settings.volume = payload.volume
    db.commit()
    return {"status": "ok"}


@app.post("/alerts/panic")
async def panic(
    payload: PanicRequest,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    print(f"[ALERT] panic request for team={payload.team_id}")
    user = _require_token(token, authorization, db)
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id, TeamMember.team_id == payload.team_id
    ).first()
    if not membership and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not in team")

    now = time.time()
    if now - _user_last.get(user.id, 0) < COOLDOWN_USER_SEC:
        print("[ALERT] blocked by user cooldown")
        raise HTTPException(status_code=429, detail="User cooldown")
    if now - _team_last.get(payload.team_id, 0) < COOLDOWN_TEAM_SEC:
        print("[ALERT] blocked by team cooldown")
        raise HTTPException(status_code=429, detail="Team cooldown")
    _user_last[user.id] = now
    _team_last[payload.team_id] = now

    team = db.get(Team, payload.team_id)
    text = payload.text.strip() if payload.text else None
    message = PanicMessage(
        team_id=payload.team_id,
        sender_user_id=user.id,
        sender_name=user.username,
        event_id=str(uuid.uuid4()),
        ts=int(now * 1000),
        text=text,
    )
    await manager.broadcast(payload.team_id, message.model_dump())
    await send_telegram_message(
        team.telegram_chat_id, format_alert(team.name, user.username, text), team.telegram_bot_token
    )
    return {"status": "ok", "event_id": message.event_id}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, token: str, team_id: int, db: Session = Depends(get_db)):
    user = _get_user_by_token(db, token)
    if not user:
        await ws.close(code=1008)
        return
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id, TeamMember.team_id == team_id
    ).first()
    if not membership and user.role != "super_admin":
        await ws.close(code=1008)
        return
    await manager.connect(team_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(team_id, ws)


@app.get("/teams/{team_id}/members", response_model=list[MemberResponse])
def list_members(
    team_id: int,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id, TeamMember.team_id == team_id
    ).first()
    if not membership and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not in team")
    rows = (
        db.query(User, TeamMember)
        .join(TeamMember, TeamMember.user_id == User.id)
        .filter(TeamMember.team_id == team_id)
        .all()
    )
    result = []
    for u, tm in rows:
        result.append(MemberResponse(user_id=u.id, username=u.username, role=tm.role))
    return result


@app.delete("/teams/{team_id}/members/{user_id}")
async def remove_member(
    team_id: int,
    user_id: int,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id, TeamMember.team_id == team_id
    ).first()
    if not membership and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not in team")
    if membership and membership.role not in ("owner", "admin") and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == user_id
    ).delete()
    db.commit()
    members = _team_members_payload(db, team_id)
    print("[WS] team_update remove:", team_id)
    await manager.broadcast(team_id, {"type": "team_update", "team_id": team_id, "members": members})
    return {"status": "ok"}


@app.post("/teams/{team_id}/leave")
async def leave_team(
    team_id: int,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    db.query(TeamMember).filter(
        TeamMember.team_id == team_id, TeamMember.user_id == user.id
    ).delete()
    db.commit()
    members = _team_members_payload(db, team_id)
    print("[WS] team_update leave:", team_id)
    await manager.broadcast(team_id, {"type": "team_update", "team_id": team_id, "members": members})
    return {"status": "ok"}


@app.post("/teams/{team_id}/invite", response_model=TeamResponse)
def rotate_invite(
    team_id: int,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id, TeamMember.team_id == team_id
    ).first()
    if not membership and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not in team")
    if membership and membership.role not in ("owner", "admin") and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team.join_code = f"TEAM-{uuid.uuid4().hex[:8]}"
    db.commit()
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        owner_user_id=team.owner_user_id,
        join_code=team.join_code,
        telegram_chat_id=team.telegram_chat_id,
        role=membership.role if membership else None,
    )


@app.post("/teams/{team_id}/telegram_test")
async def telegram_test(
    team_id: int,
    token: str | None = None,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = _require_token(token, authorization, db)
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id, TeamMember.team_id == team_id
    ).first()
    if not membership and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not in team")
    if membership and membership.role not in ("owner", "admin") and user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    team = db.get(Team, team_id)
    if not team or not team.telegram_chat_id or not team.telegram_bot_token:
        raise HTTPException(status_code=400, detail="Telegram not configured")
    await send_telegram_message(
        team.telegram_chat_id, "\u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0438\u043b\u0441\u044f \u0438 \u0433\u043e\u0442\u043e\u0432 \u043a \u0440\u0430\u0431\u043e\u0442\u0435", team.telegram_bot_token
    )
    return {"status": "ok"}

