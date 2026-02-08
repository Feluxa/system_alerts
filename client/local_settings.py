import json
import os


def _settings_path():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    folder = os.path.join(base, "PanicAlert")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "settings.json")


def load_settings():
    path = _settings_path()
    if not os.path.exists(path):
        return {
            "theme": "dark",
            "hotkey": "",
            "sound_path": "",
            "system_sound": "Siren",
            "volume": 70,
            "auto_start": False,
        }
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "theme": data.get("theme", "dark"),
            "hotkey": data.get("hotkey", ""),
            "sound_path": data.get("sound_path", ""),
            "system_sound": data.get("system_sound", "Siren"),
            "volume": int(data.get("volume", 70)),
            "auto_start": bool(data.get("auto_start", False)),
        }
    except Exception:
        return {
            "theme": "dark",
            "hotkey": "",
            "sound_path": "",
            "system_sound": "Siren",
            "volume": 70,
            "auto_start": False,
        }


def save_settings(theme, hotkey, sound_path, system_sound, volume, auto_start=False):
    path = _settings_path()
    data = {
        "theme": theme or "dark",
        "hotkey": hotkey or "",
        "sound_path": sound_path or "",
        "system_sound": system_sound or "Siren",
        "volume": int(volume),
        "auto_start": bool(auto_start),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
