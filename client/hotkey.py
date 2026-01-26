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

    def start(self):
        if keyboard is None:
            return
        if self._listener:
            return

        def _on_press(key):
            if self._match(key):
                self.on_trigger()

        self._listener = keyboard.Listener(on_press=_on_press)
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

    def update_key(self, key_text: str):
        self.key_text = key_text

    def _match(self, key):
        if not self.key_text:
            return False
        text = self.key_text.lower().replace(" ", "")
        aliases = {
            "pgup": "page_up",
            "pgdn": "page_down",
            "pageup": "page_up",
            "pagedown": "page_down",
            "esc": "escape",
        }
        text = aliases.get(text, text)
        try:
            if hasattr(key, "char") and key.char:
                return key.char.lower() == text
        except Exception:
            pass
        try:
            key_name = str(key).replace("Key.", "").lower()
            return key_name == text.lower()
        except Exception:
            return False
