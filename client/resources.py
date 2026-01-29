from pathlib import Path
import sys


def resource_path(*parts: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path.cwd()))
    return base.joinpath(*parts)
