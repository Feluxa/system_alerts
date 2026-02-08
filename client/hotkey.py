import os
import threading
from typing import Callable, Optional


class GlobalHotkey:
    def __init__(self, key_text: str, on_trigger: Callable[[], None]):
        self.key_text = key_text or ""
        self.on_trigger = on_trigger
        self._is_windows = os.name == "nt"
        self._running = False

        # Windows backend state
        self._thread: Optional[threading.Thread] = None
        self._stop_event: Optional[threading.Event] = None
        self._thread_id: int = 0
        self._mods: int = 0
        self._vk: int = 0
        self._hotkey_id = 1

        # Fallback backend for non-Windows
        self._listener = None
        if not self._is_windows:
            try:
                from pynput import keyboard as _keyboard  # type: ignore
                self._kb = _keyboard
            except Exception:
                self._kb = None
            self._pressed: set[tuple] = set()
            self._required_mods: set[tuple] = set()
            self._target_key: Optional[tuple] = None

    def start(self):
        if self._running:
            return
        self._running = True
        if self._is_windows:
            self._start_windows()
        else:
            self._start_fallback()

    def stop(self):
        if not self._running:
            return
        if self._is_windows:
            self._stop_windows()
        else:
            self._stop_fallback()
        self._running = False

    def update_key(self, key_text: str):
        self.key_text = key_text or ""
        was_running = self._running
        if was_running:
            self.stop()
        if was_running:
            self.start()

    # -------------------- Windows backend --------------------
    def _start_windows(self):
        parsed = self._parse_windows_hotkey(self.key_text)
        if parsed is None:
            return
        self._mods, self._vk = parsed
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._windows_loop, name="GlobalHotkeyWin", daemon=True)
        self._thread.start()

    def _stop_windows(self):
        if self._stop_event is not None:
            self._stop_event.set()
        # WM_QUIT = 0x0012
        if self._thread_id:
            try:
                import ctypes

                ctypes.windll.user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)
            except Exception:
                pass
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        self._thread = None
        self._stop_event = None
        self._thread_id = 0

    def _windows_loop(self):
        try:
            import ctypes
            from ctypes import wintypes
        except Exception:
            return

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        self._thread_id = int(kernel32.GetCurrentThreadId())

        # MOD_ALT=0x1, MOD_CONTROL=0x2, MOD_SHIFT=0x4, MOD_WIN=0x8, MOD_NOREPEAT=0x4000
        if not user32.RegisterHotKey(None, self._hotkey_id, self._mods | 0x4000, self._vk):
            return

        msg = wintypes.MSG()
        try:
            while self._stop_event is not None and not self._stop_event.is_set():
                ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if ret <= 0:
                    break
                # WM_HOTKEY = 0x0312
                if msg.message == 0x0312 and msg.wParam == self._hotkey_id:
                    try:
                        self.on_trigger()
                    except Exception:
                        pass
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, self._hotkey_id)

    def _parse_windows_hotkey(self, text: str) -> Optional[tuple[int, int]]:
        if not text:
            return None
        tokens = self._tokenize(text)
        if not tokens:
            return None

        mods = 0
        key_token = None
        for token in tokens:
            norm = self._normalize_token(token)
            if norm == "ctrl":
                mods |= 0x0002
                continue
            if norm == "alt":
                mods |= 0x0001
                continue
            if norm == "shift":
                mods |= 0x0004
                continue
            if norm in ("cmd", "win"):
                mods |= 0x0008
                continue
            key_token = norm

        if not key_token:
            return None

        vk = self._token_to_vk(key_token)
        if vk is None:
            return None
        return mods, vk

    def _token_to_vk(self, token: str) -> Optional[int]:
        special = {
            "backspace": 0x08,
            "tab": 0x09,
            "enter": 0x0D,
            "pause": 0x13,
            "capslock": 0x14,
            "escape": 0x1B,
            "space": 0x20,
            "pageup": 0x21,
            "pagedown": 0x22,
            "end": 0x23,
            "home": 0x24,
            "left": 0x25,
            "up": 0x26,
            "right": 0x27,
            "down": 0x28,
            "insert": 0x2D,
            "delete": 0x2E,
            "num0": 0x60,
            "num1": 0x61,
            "num2": 0x62,
            "num3": 0x63,
            "num4": 0x64,
            "num5": 0x65,
            "num6": 0x66,
            "num7": 0x67,
            "num8": 0x68,
            "num9": 0x69,
            "multiply": 0x6A,
            "add": 0x6B,
            "separator": 0x6C,
            "subtract": 0x6D,
            "decimal": 0x6E,
            "divide": 0x6F,
            "menu": 0x5D,
            ";": 0xBA,
            "=": 0xBB,
            ",": 0xBC,
            "-": 0xBD,
            ".": 0xBE,
            "/": 0xBF,
            "`": 0xC0,
            "[": 0xDB,
            "\\": 0xDC,
            "]": 0xDD,
            "'": 0xDE,
            "+": 0xBB,
        }
        if token in special:
            return special[token]
        if token.startswith("f") and token[1:].isdigit():
            idx = int(token[1:])
            if 1 <= idx <= 24:
                return 0x70 + idx - 1
        if len(token) == 1:
            ch = token.upper()
            if "A" <= ch <= "Z" or "0" <= ch <= "9":
                return ord(ch)
        return None

    # -------------------- Fallback backend (non-Windows) --------------------
    def _start_fallback(self):
        if self._kb is None or self._listener:
            return
        self._parse_fallback_hotkey()
        self._listener = self._kb.Listener(on_press=self._on_press_fallback, on_release=self._on_release_fallback)
        self._listener.start()

    def _stop_fallback(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._pressed.clear()

    def _parse_fallback_hotkey(self):
        self._required_mods = set()
        self._target_key = None
        if self._kb is None:
            return
        tokens = self._tokenize(self.key_text)
        if not tokens:
            return
        non_mod_tokens: list[str] = []
        for token in tokens:
            norm = self._normalize_token(token)
            mod_id = self._fallback_modifier_id(norm)
            if mod_id is not None:
                self._required_mods.add(mod_id)
            else:
                non_mod_tokens.append(norm)
        if not non_mod_tokens:
            return
        self._target_key = self._fallback_token_to_key_id(non_mod_tokens[-1])

    def _on_press_fallback(self, key):
        key_id = self._fallback_key_to_id(key)
        if key_id is None:
            return
        self._pressed.add(key_id)
        if self._target_key is not None and key_id == self._target_key and self._required_mods.issubset(self._pressed):
            try:
                self.on_trigger()
            except Exception:
                pass

    def _on_release_fallback(self, key):
        key_id = self._fallback_key_to_id(key)
        if key_id is not None:
            self._pressed.discard(key_id)

    def _fallback_modifier_id(self, token: str) -> Optional[tuple]:
        if self._kb is None:
            return None
        mapping = {
            "ctrl": ("key", self._kb.Key.ctrl),
            "shift": ("key", self._kb.Key.shift),
            "alt": ("key", self._kb.Key.alt),
            "cmd": ("key", self._kb.Key.cmd),
        }
        return mapping.get(token)

    def _fallback_token_to_key_id(self, token: str) -> Optional[tuple]:
        if self._kb is None:
            return None
        if len(token) == 1:
            return ("char", token.lower())
        attr = token
        if token == "pageup":
            attr = "page_up"
        elif token == "pagedown":
            attr = "page_down"
        elif token == "escape":
            attr = "esc"
        if hasattr(self._kb.Key, attr):
            return ("key", getattr(self._kb.Key, attr))
        return None

    def _fallback_key_to_id(self, key) -> Optional[tuple]:
        if self._kb is None:
            return None
        if isinstance(key, self._kb.KeyCode):
            if key.char:
                return ("char", key.char.lower())
            return None
        if isinstance(key, self._kb.Key):
            return ("key", key)
        return None

    # -------------------- shared helpers --------------------
    def _tokenize(self, text: str) -> list[str]:
        parts = [chunk.strip() for chunk in text.split("+")]
        tokens: list[str] = []
        for part in parts:
            tokens.append(part if part else "+")
        return tokens

    def _normalize_token(self, token: str) -> str:
        aliases = {
            "control": "ctrl",
            "ctl": "ctrl",
            "option": "alt",
            "command": "cmd",
            "meta": "cmd",
            "win": "win",
            "windows": "win",
            "pgup": "pageup",
            "page up": "pageup",
            "pgdn": "pagedown",
            "page down": "pagedown",
            "esc": "escape",
            "del": "delete",
            "ins": "insert",
            "return": "enter",
            "spacebar": "space",
            "left arrow": "left",
            "right arrow": "right",
            "up arrow": "up",
            "down arrow": "down",
            "num 0": "num0",
            "num 1": "num1",
            "num 2": "num2",
            "num 3": "num3",
            "num 4": "num4",
            "num 5": "num5",
            "num 6": "num6",
            "num 7": "num7",
            "num 8": "num8",
            "num 9": "num9",
        }
        key = token.strip().lower()
        return aliases.get(key, key)
