import asyncio
import threading
from typing import Callable, Optional

import websockets


class WSClient:
    def __init__(self, url: str, on_message: Callable[[dict], None]):
        self.url = url
        self.on_message = on_message
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._last_error = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        asyncio.run(self._loop())

    async def _loop(self):
        while not self._stop.is_set():
            try:
                async with websockets.connect(self.url, ping_interval=20, ping_timeout=20) as ws:
                    async def _heartbeat():
                        while not self._stop.is_set():
                            try:
                                await ws.send("ping")
                            except Exception:
                                return
                            await asyncio.sleep(15)

                    hb_task = asyncio.create_task(_heartbeat())
                    while not self._stop.is_set():
                        msg = await ws.recv()
                        if msg:
                            try:
                                import json

                                payload = json.loads(msg)
                                self.on_message(payload)
                            except Exception:
                                pass
                    hb_task.cancel()
            except Exception:
                self._last_error = True
                await asyncio.sleep(2)
