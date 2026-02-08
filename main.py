import signal
import sys
from client.resources import resource_path

from PySide6 import QtCore, QtGui, QtWidgets

from client.api import ApiClient
from client.session_store import (
    clear_active,
    get_active_profile,
    list_profiles,
    remove_profile,
    upsert_profile,
)
from client.version import CLIENT_VERSION
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from ui.style import apply_theme


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Panic Alert BETA 2.0")
    apply_theme(app, "dark")

    icon = _load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)

    api_client = ApiClient()
    if not _check_client_version(api_client):
        return

    while True:
        user = _restore_active_session(api_client)
        if not user:
            dialog = LoginDialog(api_client, icon, profiles=list_profiles())
            if dialog.exec() != QtWidgets.QDialog.Accepted or not dialog.user:
                return
            user = dialog.user
            if dialog.remember_login:
                upsert_profile(user, api_client.token or "", api_client.base_url, make_active=True)
            else:
                remove_profile(user.get("username", ""))
                clear_active()

        apply_theme(app, "dark")
        window = MainWindow(api_client, user)

        def _handle_exit(*_):
            window.request_quit()

        signal.signal(signal.SIGINT, _handle_exit)
        signal.signal(signal.SIGTERM, _handle_exit)
        window.show()
        app.exec()
        if window.next_action == "logout":
            api_client.token = None
            continue
        return


def _load_app_icon() -> QtGui.QIcon:
    for name in ("photo.png", "photo.jpg", "photo.jpeg"):
        path = resource_path("assets", "photos", name)
        if path.exists():
            return QtGui.QIcon(str(path))
    return QtGui.QIcon()


def _restore_active_session(api_client: ApiClient):
    profile = get_active_profile()
    if not profile:
        return None
    api_client.base_url = profile.get("base_url") or api_client.base_url
    api_client.token = profile.get("token")
    if not api_client.token:
        clear_active()
        return None
    try:
        # Any protected endpoint validates token and quickly tells us if it expired/invalid.
        api_client.my_team()
    except Exception:
        remove_profile(profile.get("username", ""))
        clear_active()
        api_client.token = None
        return None
    return {
        "id": profile.get("user_id"),
        "username": profile.get("username"),
        "role": profile.get("role", "user"),
    }


def _parse_version(version: str):
    parts = []
    for raw in (version or "").split("."):
        try:
            parts.append(int(raw))
        except Exception:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def _is_outdated(current: str, minimum: str):
    return _parse_version(current) < _parse_version(minimum)


def _check_client_version(api_client: ApiClient):
    try:
        info = api_client.get_version_info()
    except Exception:
        QtWidgets.QMessageBox.critical(
            None,
            "Version check failed",
            "Cannot verify client version. Check server connection and try again.",
        )
        return False

    min_version = str(info.get("min_client_version", "0.0.0"))
    latest_version = str(info.get("latest_client_version", min_version))
    download_url = str(info.get("download_url", ""))
    hard_block = bool(info.get("hard_block", True))
    if not _is_outdated(CLIENT_VERSION, min_version):
        return True
    if hard_block:
        _show_update_required_dialog(latest_version, download_url)
        return False
    _show_update_recommended_dialog(latest_version, download_url)
    return True


def _show_update_required_dialog(latest_version: str, download_url: str):
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("Update required")
    dialog.setFixedSize(460, 220)
    layout = QtWidgets.QVBoxLayout(dialog)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)

    title = QtWidgets.QLabel("A newer client version is required.")
    title.setObjectName("sectionTitle")
    title.setWordWrap(True)
    layout.addWidget(title)

    info = QtWidgets.QLabel(
        f"Current: {CLIENT_VERSION}\nRequired: {latest_version}\nInstall the latest build to continue."
    )
    info.setWordWrap(True)
    info.setObjectName("statusLabel")
    layout.addWidget(info)

    url = QtWidgets.QLineEdit(download_url)
    url.setReadOnly(True)
    layout.addWidget(url)

    button_row = QtWidgets.QHBoxLayout()
    open_btn = QtWidgets.QPushButton("Open download page")
    close_btn = QtWidgets.QPushButton("Close")
    button_row.addWidget(open_btn)
    button_row.addStretch(1)
    button_row.addWidget(close_btn)
    layout.addLayout(button_row)

    def _open_download():
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(download_url))

    open_btn.clicked.connect(_open_download)
    close_btn.clicked.connect(dialog.reject)
    dialog.exec()


def _show_update_recommended_dialog(latest_version: str, download_url: str):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setWindowTitle("Update recommended")
    msg.setText(
        f"Current: {CLIENT_VERSION}\nRecommended: {latest_version}\nYou can continue, but update is recommended."
    )
    if download_url:
        msg.setInformativeText(download_url)
        open_btn = msg.addButton("Open download page", QtWidgets.QMessageBox.ActionRole)
        msg.addButton("Continue", QtWidgets.QMessageBox.AcceptRole)
        msg.exec()
        if msg.clickedButton() == open_btn:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(download_url))
        return
    msg.exec()


if __name__ == "__main__":
    main()
