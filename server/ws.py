import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._rooms = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, team_id: int, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._rooms[team_id].add(ws)

    async def disconnect(self, team_id: int, ws: WebSocket):
        async with self._lock:
            if ws in self._rooms.get(team_id, set()):
                self._rooms[team_id].remove(ws)

    async def broadcast(self, team_id: int, payload: dict):
        async with self._lock:
            conns = list(self._rooms.get(team_id, set()))
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                await self.disconnect(team_id, ws)
