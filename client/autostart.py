import platform
import sys
from pathlib import Path


APP_RUN_KEY = "PanicAlert"


def is_supported() -> bool:
    return platform.system() == "Windows"


def _windows_startup_command() -> str:
    # When frozen, launch the built executable; in dev mode, launch main.py.
    if getattr(sys, "frozen", False):
        return f"\"{sys.executable}\""
    root = Path(__file__).resolve().parent.parent
    main_py = root / "main.py"
    python_exe = Path(sys.executable)
    return f"\"{python_exe}\" \"{main_py}\""


def set_enabled(enabled: bool):
    if platform.system() != "Windows":
        return
    import winreg

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, APP_RUN_KEY, 0, winreg.REG_SZ, _windows_startup_command())
        else:
            try:
                winreg.DeleteValue(key, APP_RUN_KEY)
            except FileNotFoundError:
                pass


def get_enabled() -> bool:
    if platform.system() != "Windows":
        return False
    import winreg

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_RUN_KEY)
            return bool(value)
    except FileNotFoundError:
        return False
