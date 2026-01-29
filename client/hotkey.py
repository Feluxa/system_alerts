from typing import Callable, Optional

try:
    from pynput import keyboard
except Exception:  # pragma: no cover
    keyboard = None


class GlobalHotkey:
    def __init__(self, key_text: str, on_trigger: Callable[[], None]):
        self.key_text = key_text
        self.on_trigger = on_trigger
        self._listener: Optional["keyboard.Listener"] = None
        self._hotkey: Optional["keyboard.HotKey"] = None
        self._build_hotkey()

    def start(self):
        if keyboard is None:
            return
        if self._listener:
            return

        def _on_press(key):
            if self._hotkey:
                if self._listener:
                    self._hotkey.press(self._listener.canonical(key))
                else:
                    self._hotkey.press(key)

        def _on_release(key):
            if self._hotkey:
                if self._listener:
                    self._hotkey.release(self._listener.canonical(key))
                else:
                    self._hotkey.release(key)

        self._listener = keyboard.Listener(on_press=_on_press, on_release=_on_release)
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

    def update_key(self, key_text: str):
        self.key_text = key_text
        self._build_hotkey()

    def _normalize_token(self, token: str) -> str:
        aliases = {
            "pgup": "page_up",
            "pgdn": "page_down",
            "pageup": "page_up",
            "pagedown": "page_down",
            "esc": "escape",
            "del": "delete",
            "control": "ctrl",
            "cmd": "cmd",
            "meta": "cmd",
            "win": "cmd",
            "windows": "cmd",
            "option": "alt",
            "return": "enter",
            "spacebar": "space",
        }
        token = token.lower()
        return aliases.get(token, token)

    def _to_pynput_hotkey(self, text: str) -> Optional[str]:
        if not text:
            return None
        parts = [p for p in text.split("+") if p.strip()]
        out_parts: list[str] = []
        for part in parts:
            token = self._normalize_token(part.strip())
            if token in {"ctrl", "shift", "alt", "cmd"}:
                out_parts.append(f"<{token}>")
                continue
            token = token.lower()
            if token.startswith("f") and token[1:].isdigit():
                out_parts.append(f"<{token}>")
                continue
            if token in {
                "enter",
                "tab",
                "space",
                "backspace",
                "delete",
                "home",
                "end",
                "insert",
                "page_up",
                "page_down",
                "up",
                "down",
                "left",
                "right",
                "esc",
                "escape",
            }:
                out_parts.append(f"<{token}>")
                continue
            if len(token) == 1:
                out_parts.append(token)
                continue
            # punctuation or unknown token, try as-is
            out_parts.append(token)
        return "+".join(out_parts) if out_parts else None

    def _build_hotkey(self):
        if keyboard is None:
            self._hotkey = None
            return
        hotkey_text = self._to_pynput_hotkey(self.key_text)
        if not hotkey_text:
            self._hotkey = None
            return
        try:
            keys = keyboard.HotKey.parse(hotkey_text)
        except Exception:
            self._hotkey = None
            return
        self._hotkey = keyboard.HotKey(keys, self.on_trigger)
