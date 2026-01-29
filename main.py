import signal
import sys
from pathlib import Path

from PySide6 import QtGui, QtWidgets

from client.api import ApiClient
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from ui.style import apply_theme


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Panic Alert BETA")
    apply_theme(app, "dark")

    icon = _load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)

    api_client = ApiClient()
    dialog = LoginDialog(api_client, icon)
    if dialog.exec() == QtWidgets.QDialog.Accepted and dialog.user:
        apply_theme(app, "dark")
        window = MainWindow(api_client, dialog.user)
        def _handle_exit(*_):
            window.request_quit()
        signal.signal(signal.SIGINT, _handle_exit)
        signal.signal(signal.SIGTERM, _handle_exit)
        window.show()
        sys.exit(app.exec())


def _load_app_icon() -> QtGui.QIcon:
    base = Path.cwd() / "assets" / "photos"
    for name in ("photo.png", "photo.jpg", "photo.jpeg"):
        path = base / name
        if path.exists():
            return QtGui.QIcon(str(path))
    return QtGui.QIcon()


if __name__ == "__main__":
    main()
