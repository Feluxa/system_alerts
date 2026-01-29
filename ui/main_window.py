from PySide6 import QtCore, QtGui, QtWidgets

from client.hotkey import GlobalHotkey
from client.local_settings import load_settings, save_settings
from client.ws_client import WSClient
from ui.alerts import AlertPage
from ui.invites import InvitePage
from ui.settings import SettingsPage
from ui.teams import TeamsPage
from ui.titlebar import TitleBar
from ui.sidebar import Sidebar


APP_NAME = "Panic Alert BETA"


class MainWindow(QtWidgets.QMainWindow):
    ws_message = QtCore.Signal(dict)
    ws_status = QtCore.Signal(bool)
    def __init__(self, api_client, current_user):
        super().__init__()
        self.api = api_client
        self.current_user = current_user

        self.setWindowTitle(APP_NAME)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        self.setMinimumSize(980, 640)
        self._set_app_icon()
        self._resize_margin = 6
        self._resizing = False
        self._resize_edges = set()
        self._press_pos = None
        self._start_geo = None
        self.setMouseTracking(True)

        container = QtWidgets.QFrame()
        container.setObjectName("windowFrame")
        self.setCentralWidget(container)
        container.setMouseTracking(True)

        self.title_bar = TitleBar(APP_NAME, self)

        self.sidebar = Sidebar()
        self.sidebar.nav_changed.connect(self._on_nav_changed)
        self.sidebar.account_requested.connect(self._open_settings)
        self.sidebar.setMouseTracking(True)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.setMouseTracking(True)
        self.pages = {}

        self.alert_page = AlertPage()
        self.alert_page.panic_btn.clicked.connect(self._send_panic)
        self.alert_page.send_btn.clicked.connect(self._send_text_alert)
        self.alert_page.text_input.returnPressed.connect(self._send_text_alert)
        self.pages["alert"] = self.alert_page
        self.stack.addWidget(self.alert_page)

        self.teams_page = TeamsPage(self.api)
        self.teams_page.set_current_user(current_user)
        self.teams_page.team_changed.connect(self._on_team_changed)
        self.pages["teams"] = self.teams_page
        self.stack.addWidget(self.teams_page)

        self.settings_page = SettingsPage()
        self.settings_page.theme_changed.connect(self._handle_theme_change)
        self.settings_page.settings_saved.connect(self._handle_settings_save)
        self.pages["settings"] = self.settings_page
        self.stack.addWidget(self.settings_page)
        settings = load_settings()
        self.settings_page.set_theme(settings.get("theme", "dark"))
        self.settings_page.set_settings(
            settings.get("hotkey", ""),
            settings.get("sound_path", ""),
            settings.get("system_sound", "Siren"),
            settings.get("volume", 70),
        )
        self._apply_theme(settings.get("theme", "dark"))
        self.alert_page.set_hotkey(settings.get("hotkey", ""))

        if current_user["role"] == "super_admin":
            self.invite_page = InvitePage(self.api)
            self.pages["invites"] = self.invite_page
            self.stack.addWidget(self.invite_page)
        else:
            self.invite_page = None

        self._configure_sidebar()

        body = QtWidgets.QHBoxLayout()
        body.setContentsMargins(12, 10, 12, 6)
        body.setSpacing(12)
        body.addWidget(self.sidebar)
        body.addWidget(self.stack, stretch=1)

        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.title_bar)
        layout.addLayout(body, stretch=1)

        self.resize_grip = QtWidgets.QSizeGrip(container)
        layout.addWidget(self.resize_grip, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        for widget in (container, self.sidebar, self.stack, self.title_bar):
            widget.installEventFilter(self)

        self._ws_client = None
        self._ws_ready = False
        self.ws_message.connect(self._handle_ws_message)
        self.ws_status.connect(self._handle_ws_status)
        self._hotkey = GlobalHotkey(settings.get("hotkey", ""), self._send_panic)
        self._hotkey.start()
        self._start_ws()
        self._allow_quit = False
        self._setup_tray()

    def closeEvent(self, event):
        try:
            if self._tray and self._tray.isVisible() and not self._allow_quit:
                self.hide()
                event.ignore()
                return
            if self._ws_client:
                self._ws_client.stop()
            if self._hotkey:
                self._hotkey.stop()
        finally:
            if not event.isAccepted():
                return
            super().closeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            edges = self._hit_test_edges(event.position().toPoint())
            if edges:
                self._resizing = True
                self._resize_edges = edges
                self._press_pos = event.globalPosition().toPoint()
                self._start_geo = self.geometry()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        if self._resizing and self._start_geo is not None:
            self._perform_resize(event.globalPosition().toPoint())
            event.accept()
            return
        edges = self._hit_test_edges(pos)
        self._update_cursor(edges)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._resizing:
            self._resizing = False
            self._resize_edges = set()
            self._press_pos = None
            self._start_geo = None
            self._update_cursor(set())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def eventFilter(self, watched, event):
        if isinstance(event, QtGui.QMouseEvent):
            if event.type() == QtCore.QEvent.MouseButtonPress:
                local = watched.mapTo(self, event.position().toPoint())
                if event.button() == QtCore.Qt.LeftButton:
                    edges = self._hit_test_edges(local)
                    if edges:
                        self._resizing = True
                        self._resize_edges = edges
                        self._press_pos = event.globalPosition().toPoint()
                        self._start_geo = self.geometry()
                        return True
            elif event.type() == QtCore.QEvent.MouseMove:
                local = watched.mapTo(self, event.position().toPoint())
                if self._resizing and self._start_geo is not None:
                    self._perform_resize(event.globalPosition().toPoint())
                    return True
                edges = self._hit_test_edges(local)
                self._update_cursor(edges)
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                if self._resizing:
                    self._resizing = False
                    self._resize_edges = set()
                    self._press_pos = None
                    self._start_geo = None
                    self._update_cursor(set())
                    return True
        return super().eventFilter(watched, event)

    def _hit_test_edges(self, pos):
        rect = self.rect()
        margin = self._resize_margin
        edges = set()
        if pos.x() <= rect.left() + margin:
            edges.add("left")
        if pos.x() >= rect.right() - margin:
            edges.add("right")
        if pos.y() <= rect.top() + margin:
            edges.add("top")
        if pos.y() >= rect.bottom() - margin:
            edges.add("bottom")
        return edges

    def _update_cursor(self, edges):
        if not edges:
            self.unsetCursor()
            return
        if {"left", "top"} <= edges or {"right", "bottom"} <= edges:
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        elif {"right", "top"} <= edges or {"left", "bottom"} <= edges:
            self.setCursor(QtCore.Qt.SizeBDiagCursor)
        elif "left" in edges or "right" in edges:
            self.setCursor(QtCore.Qt.SizeHorCursor)
        elif "top" in edges or "bottom" in edges:
            self.setCursor(QtCore.Qt.SizeVerCursor)

    def _perform_resize(self, global_pos):
        if not self._start_geo or not self._press_pos:
            return
        dx = global_pos.x() - self._press_pos.x()
        dy = global_pos.y() - self._press_pos.y()
        rect = self._start_geo
        min_w = self.minimumWidth()
        min_h = self.minimumHeight()

        x = rect.x()
        y = rect.y()
        w = rect.width()
        h = rect.height()

        if "left" in self._resize_edges:
            new_w = w - dx
            if new_w >= min_w:
                x = rect.x() + dx
                w = new_w
        if "right" in self._resize_edges:
            new_w = w + dx
            if new_w >= min_w:
                w = new_w
        if "top" in self._resize_edges:
            new_h = h - dy
            if new_h >= min_h:
                y = rect.y() + dy
                h = new_h
        if "bottom" in self._resize_edges:
            new_h = h + dy
            if new_h >= min_h:
                h = new_h

        self.setGeometry(x, y, w, h)

    def _configure_sidebar(self):
        items = [
            ("alert", "Alert"),
            ("teams", "Teams"),
        ]
        if self.invite_page is not None:
            items.append(("invites", "Invites"))
        self.sidebar.set_items(items)
        self.sidebar.set_profile(self.current_user["username"], self.current_user["role"])

    def _open_default_page(self):
        self._on_nav_changed("alert")

    def _on_nav_changed(self, key):
        page = self.pages.get(key)
        if page is None:
            return
        self.stack.setCurrentWidget(page)
        self.sidebar.set_active(key)

    def _open_settings(self):
        self._on_nav_changed("settings")

    def _handle_theme_change(self, theme):
        if not self.current_user:
            return
        save_settings(
            theme=theme,
            hotkey=self.settings_page.hotkey.text().strip(),
            sound_path=self.settings_page.sound_custom_path.text().strip(),
            system_sound=self.settings_page.sound_select.currentText(),
            volume=self.settings_page.volume.value(),
        )
        self._apply_theme(theme)

    def _apply_theme(self, theme):
        from ui.style import apply_theme
        apply_theme(QtWidgets.QApplication.instance(), theme)

    def _set_app_icon(self):
        base = QtCore.QDir.currentPath()
        for name in ("photo.png", "photo.jpg", "photo.jpeg"):
            path = QtCore.QDir(base).filePath(f"assets/photos/{name}")
            if QtCore.QFileInfo(path).exists():
                icon = QtGui.QIcon(path)
                self.setWindowIcon(icon)
                QtWidgets.QApplication.instance().setWindowIcon(icon)
                return

    def _setup_tray(self):
        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            self._tray = None
            return
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.setQuitOnLastWindowClosed(False)
        self._tray = QtWidgets.QSystemTrayIcon(self.windowIcon(), self)
        menu = QtWidgets.QMenu()
        action_show = menu.addAction("Open")
        action_quit = menu.addAction("Quit")
        action_show.triggered.connect(self._tray_show)
        action_quit.triggered.connect(self._tray_quit)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._tray_activated)
        self._tray.show()

    def _tray_show(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _tray_quit(self):
        if self._tray:
            self._tray.hide()
        self._allow_quit = True
        self.close()
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.quit()

    def _tray_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self._tray_show()

    def minimize_to_tray(self):
        if self._tray and self._tray.isVisible():
            self.hide()
        else:
            self.showMinimized()

    def request_quit(self):
        if self._tray:
            self._tray.hide()
        self._allow_quit = True
        self.close()
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.quit()

    def _handle_settings_save(self, hotkey, sound_path, system_sound, volume):
        if not self.current_user:
            return
        current_theme = self.settings_page.theme_select.currentText().lower()
        save_settings(current_theme, hotkey, sound_path, system_sound, volume)
        self._hotkey.update_key(hotkey)
        self.alert_page.set_hotkey(hotkey)

    def _start_ws(self):
        try:
            team = self.api.my_team()
        except Exception:
            team = None
        if not team:
            self.alert_page.set_ws_status(False)
            return
        ws_base = self.api.base_url.replace("http://", "ws://").replace("https://", "wss://")
        url = f"{ws_base}/ws?token={self.api.token}&team_id={team['id']}"
        self._ws_client = WSClient(url, self._on_ws_message, self._on_ws_status)
        self._ws_client.start()
        self._ws_ready = True
        self.alert_page.set_hotkey(self.settings_page.hotkey.text().strip())

    def _on_ws_message(self, payload):
        self.ws_message.emit(payload)

    def _on_ws_status(self, connected: bool):
        self.ws_status.emit(connected)

    def _handle_ws_status(self, connected: bool):
        self.alert_page.set_ws_status(connected)

    def _handle_ws_message(self, payload):
        msg_type = payload.get("type")
        if msg_type == "panic_alert":
            self.settings_page._test_sound()
            return
        if msg_type == "team_update":
            members = payload.get("members")
            team_info = payload.get("team")
            if team_info:
                self.teams_page.apply_team_update(team_info, members)
                return
            if isinstance(members, list):
                self.teams_page.apply_member_update(members)
            else:
                self.teams_page.refresh_teams()

    def _send_panic(self):
        try:
            team = self.api.my_team()
            if team:
                self.api.send_panic(team["id"])
                self.alert_page.set_status("Alert sent.")
            else:
                self.alert_page.set_status("No team selected.")
        except Exception:
            self.alert_page.set_status("Alert failed. Check server logs.")

    def _send_text_alert(self):
        text = self.alert_page.text_input.text().strip()
        if not text:
            return
        try:
            team = self.api.my_team()
            if team:
                self.api.send_panic(team["id"], text=text)
                self.alert_page.text_input.clear()
                self.alert_page.set_status("Text alert sent.")
            else:
                self.alert_page.set_status("No team selected.")
        except Exception:
            self.alert_page.set_status("Text alert failed. Check server logs.")

    def _on_team_changed(self, team_id: int):
        if self._ws_client:
            self._ws_client.stop()
            self._ws_client = None
        if team_id:
            self._start_ws()
