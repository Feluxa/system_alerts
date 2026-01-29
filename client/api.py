import os
from typing import Any, Dict, Optional

import httpx


class ApiClient:
    def __init__(self, base_url: Optional[str] = None):
        # http://127.0.0.1:8000
        # http://45.95.0.98:8000
        self.base_url = base_url or os.getenv("ALERTS_API_URL", "http://45.95.0.98:8000")
        self.token: Optional[str] = None

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}{path}"

    def _headers(self) -> Dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def register(self, invite_code: str, username: str, password: str) -> Dict[str, Any]:
        resp = httpx.post(
            self._url("/auth/register"),
            json={"invite_code": invite_code, "username": username, "password": password},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self.token = data["token"]
        return data

    def login(self, username: str, password: str) -> Dict[str, Any]:
        resp = httpx.post(
            self._url("/auth/login"),
            json={"username": username, "password": password},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self.token = data["token"]
        return data

    def my_team(self) -> Optional[Dict[str, Any]]:
        resp = httpx.get(self._url("/teams/my"), headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def create_team(self, name: str, description: str | None) -> Dict[str, Any]:
        resp = httpx.post(
            self._url("/teams/create"),
            json={"name": name, "description": description},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def join_team(self, join_code: str) -> Dict[str, Any]:
        resp = httpx.post(
            self._url("/teams/join"),
            json={"join_code": join_code},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def list_members(self, team_id: int) -> list[Dict[str, Any]]:
        resp = httpx.get(
            self._url(f"/teams/{team_id}/members"),
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def remove_member(self, team_id: int, user_id: int) -> None:
        resp = httpx.delete(
            self._url(f"/teams/{team_id}/members/{user_id}"),
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()

    def leave_team(self, team_id: int) -> None:
        resp = httpx.post(
            self._url(f"/teams/{team_id}/leave"),
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()

    def rotate_invite(self, team_id: int) -> Dict[str, Any]:
        resp = httpx.post(
            self._url(f"/teams/{team_id}/invite"),
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def set_team_telegram(self, team_id: int, chat_id: str, bot_token: str) -> Dict[str, Any]:
        resp = httpx.patch(
            self._url(f"/teams/{team_id}/telegram_chat"),
            json={"telegram_chat_id": chat_id, "telegram_bot_token": bot_token},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def update_team(self, team_id: int, name: str | None, description: str | None) -> Dict[str, Any]:
        resp = httpx.patch(
            self._url(f"/teams/{team_id}"),
            json={"name": name, "description": description},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def test_telegram(self, team_id: int) -> Dict[str, Any]:
        resp = httpx.post(
            self._url(f"/teams/{team_id}/telegram_test"),
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def get_settings(self) -> Dict[str, Any]:
        resp = httpx.get(self._url("/users/settings"), headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()

    def update_settings(self, hotkey: str, sound_path: str, system_sound: str, volume: int, theme: str | None = None) -> None:
        resp = httpx.patch(
            self._url("/users/settings"),
            json={
                "theme": theme,
                "hotkey": hotkey,
                "sound_path": sound_path,
                "system_sound": system_sound,
                "volume": volume,
            },
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()

    def send_panic(self, team_id: int, text: str | None = None, **_) -> Dict[str, Any]:
        resp = httpx.post(
            self._url("/alerts/panic"),
            json={"team_id": team_id, "text": text},
            headers=self._headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def create_invite(self) -> Dict[str, Any]:
        resp = httpx.post(self._url("/invites/create"), headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()
