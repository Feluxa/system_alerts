import json
import os
import time


def _session_path():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    folder = os.path.join(base, "PanicAlert")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "sessions.json")


def _load_data():
    path = _session_path()
    if not os.path.exists(path):
        return {"active": None, "profiles": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"active": None, "profiles": []}
        profiles = data.get("profiles", [])
        if not isinstance(profiles, list):
            profiles = []
        active = data.get("active")
        return {"active": active, "profiles": profiles}
    except Exception:
        return {"active": None, "profiles": []}


def _save_data(data):
    with open(_session_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_profiles():
    data = _load_data()
    return list(data.get("profiles", []))


def get_active_profile():
    data = _load_data()
    active = data.get("active")
    if not active:
        return None
    for profile in data.get("profiles", []):
        if profile.get("username") == active:
            return profile
    return None


def upsert_profile(user: dict, token: str, base_url: str, make_active: bool = True):
    if not user or not token:
        return
    data = _load_data()
    username = user.get("username")
    profiles = []
    found = False
    for profile in data.get("profiles", []):
        if profile.get("username") == username:
            profile = {
                "username": username,
                "user_id": user.get("id"),
                "role": user.get("role"),
                "token": token,
                "base_url": base_url,
                "updated_at": int(time.time()),
            }
            found = True
        profiles.append(profile)
    if not found:
        profiles.append(
            {
                "username": username,
                "user_id": user.get("id"),
                "role": user.get("role"),
                "token": token,
                "base_url": base_url,
                "updated_at": int(time.time()),
            }
        )
    data["profiles"] = profiles
    if make_active:
        data["active"] = username
    _save_data(data)


def set_active(username: str | None):
    data = _load_data()
    data["active"] = username
    _save_data(data)


def clear_active():
    set_active(None)


def remove_profile(username: str):
    data = _load_data()
    data["profiles"] = [p for p in data.get("profiles", []) if p.get("username") != username]
    if data.get("active") == username:
        data["active"] = None
    _save_data(data)
