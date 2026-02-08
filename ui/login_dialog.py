from PySide6 import QtCore, QtGui, QtWidgets


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, api_client, app_icon=None, profiles=None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user = None
        self.remember_login = True
        self._profiles = profiles or []

        self.setWindowTitle("Sign in")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setFixedSize(420, 560)
        self.setObjectName("loginDialog")
        self._drag_pos = None
        if app_icon is not None and not app_icon.isNull():
            self.setWindowIcon(app_icon)

        self.title = QtWidgets.QLabel("Log in or sign up")
        self.title.setObjectName("loginTitle")
        self.subtitle = QtWidgets.QLabel(
            "Get access to your team alerts and settings."
        )
        self.subtitle.setObjectName("loginSubtitle")

        self.close_btn = QtWidgets.QPushButton("X")
        self.close_btn.setObjectName("titleButtonClose")
        self.close_btn.setFixedSize(28, 24)
        self.close_btn.clicked.connect(self.reject)

        self.tabs = QtWidgets.QTabWidget()
        self.login_tab = QtWidgets.QWidget()
        self.register_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.login_tab, "Sign in")
        self.tabs.addTab(self.register_tab, "Sign up")

        self._build_login()
        self._build_register()

        self.frame = QtWidgets.QFrame()
        self.frame.setObjectName("loginFrame")
        frame_layout = QtWidgets.QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(24, 24, 24, 24)
        frame_layout.setSpacing(16)

        header = QtWidgets.QHBoxLayout()
        header.addWidget(self.title)
        header.addStretch(1)
        header.addWidget(self.close_btn)
        frame_layout.addLayout(header)
        frame_layout.addWidget(self.subtitle)
        frame_layout.addWidget(self.tabs)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self.frame)

    def _build_login(self):
        self.login_username = QtWidgets.QLineEdit()
        self.login_username.setPlaceholderText("Login")
        self.login_password = QtWidgets.QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_show_pw = QtWidgets.QToolButton()
        self.login_show_pw.setCheckable(True)
        self.login_show_pw.setIcon(self._load_icon("eye.svg"))
        self.login_show_pw.setFixedSize(28, 28)
        self.login_show_pw.setAutoRaise(True)
        self.login_show_pw.clicked.connect(self._toggle_login_password)
        self.login_btn = QtWidgets.QPushButton("Continue")
        self.login_btn.setObjectName("primaryButton")
        self.remember_box = QtWidgets.QCheckBox("Remember this profile")
        self.remember_box.setChecked(True)
        self.login_status = QtWidgets.QLabel("")
        self.login_status.setObjectName("statusLabel")
        self.login_status.setWordWrap(True)
        self.saved_profiles = QtWidgets.QComboBox()
        self.saved_profiles.setVisible(False)
        self.saved_sign_in_btn = QtWidgets.QPushButton("Use saved profile")
        self.saved_sign_in_btn.setObjectName("ghostButton")
        self.saved_sign_in_btn.clicked.connect(self._use_saved_profile)
        self.saved_sign_in_btn.setVisible(False)

        if self._profiles:
            self.saved_profiles.setVisible(True)
            self.saved_sign_in_btn.setVisible(True)
            for profile in self._profiles:
                self.saved_profiles.addItem(profile.get("username", ""), profile)

        self.login_btn.clicked.connect(self._do_login)

        layout = QtWidgets.QVBoxLayout(self.login_tab)
        layout.setSpacing(12)
        layout.addWidget(self.login_username)
        login_pw_row = QtWidgets.QHBoxLayout()
        login_pw_row.addWidget(self.login_password)
        login_pw_row.addWidget(self.login_show_pw)
        layout.addLayout(login_pw_row)
        saved_row = QtWidgets.QHBoxLayout()
        saved_row.addWidget(self.saved_profiles)
        saved_row.addWidget(self.saved_sign_in_btn)
        layout.addLayout(saved_row)
        layout.addWidget(self.remember_box)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.login_status)
        layout.addStretch(1)

    def _build_register(self):
        self.register_invite = QtWidgets.QLineEdit()
        self.register_invite.setPlaceholderText("Invite code")
        self.register_username = QtWidgets.QLineEdit()
        self.register_username.setPlaceholderText("Login")
        self.register_password = QtWidgets.QLineEdit()
        self.register_password.setPlaceholderText("Password")
        self.register_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.register_show_pw = QtWidgets.QToolButton()
        self.register_show_pw.setCheckable(True)
        self.register_show_pw.setIcon(self._load_icon("eye.svg"))
        self.register_show_pw.setFixedSize(28, 28)
        self.register_show_pw.setAutoRaise(True)
        self.register_show_pw.clicked.connect(self._toggle_register_password)
        self.register_password2 = QtWidgets.QLineEdit()
        self.register_password2.setPlaceholderText("Confirm password")
        self.register_password2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.register_show_pw2 = QtWidgets.QToolButton()
        self.register_show_pw2.setCheckable(True)
        self.register_show_pw2.setIcon(self._load_icon("eye.svg"))
        self.register_show_pw2.setFixedSize(28, 28)
        self.register_show_pw2.setAutoRaise(True)
        self.register_show_pw2.clicked.connect(self._toggle_register_password2)
        self.register_btn = QtWidgets.QPushButton("Create account")
        self.register_btn.setObjectName("primaryButton")
        self.register_status = QtWidgets.QLabel("")
        self.register_status.setObjectName("statusLabel")
        self.register_status.setWordWrap(True)

        self.register_btn.clicked.connect(self._do_register)

        layout = QtWidgets.QVBoxLayout(self.register_tab)
        layout.setSpacing(12)
        layout.addWidget(self.register_invite)
        layout.addWidget(self.register_username)
        register_pw_row = QtWidgets.QHBoxLayout()
        register_pw_row.addWidget(self.register_password)
        register_pw_row.addWidget(self.register_show_pw)
        layout.addLayout(register_pw_row)
        register_pw_row2 = QtWidgets.QHBoxLayout()
        register_pw_row2.addWidget(self.register_password2)
        register_pw_row2.addWidget(self.register_show_pw2)
        layout.addLayout(register_pw_row2)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.register_status)
        layout.addStretch(1)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & QtCore.Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def _do_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        if not username or not password:
            self.login_status.setText("Enter login and password.")
            return
        try:
            user = self.api_client.login(username, password)
        except Exception as exc:
            message = "Login failed."
            text = str(exc)
            if "401" in text:
                message = "Invalid login or password."
            elif "Failed to establish a new connection" in text or "Connection refused" in text:
                message = "Server is not reachable."
            elif "ReadTimeout" in text or "timed out" in text:
                message = "Server timeout. Try again."
            self.login_status.setText(message)
            print(f"Login failed: {exc}")
            return
        self.user = {
            "id": user.get("user_id"),
            "username": user.get("username"),
            "role": user.get("role"),
        }
        self.remember_login = self.remember_box.isChecked()
        self.accept()

    def _use_saved_profile(self):
        if self.saved_profiles.count() == 0:
            return
        profile = self.saved_profiles.currentData()
        if not isinstance(profile, dict):
            return
        token = profile.get("token")
        if not token:
            self.login_status.setText("Saved profile has no token.")
            return
        prev_base = self.api_client.base_url
        prev_token = self.api_client.token
        self.api_client.base_url = profile.get("base_url") or self.api_client.base_url
        self.api_client.token = token
        try:
            self.api_client.my_team()
        except Exception:
            self.api_client.base_url = prev_base
            self.api_client.token = prev_token
            self.login_status.setText("Saved session expired. Sign in with password.")
            return
        self.user = {
            "id": profile.get("user_id"),
            "username": profile.get("username"),
            "role": profile.get("role", "user"),
        }
        self.remember_login = True
        self.accept()

    def _toggle_login_password(self):
        if self.login_show_pw.isChecked():
            self.login_password.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.login_show_pw.setIcon(self._load_icon("eye-off.svg"))
        else:
            self.login_password.setEchoMode(QtWidgets.QLineEdit.Password)
            self.login_show_pw.setIcon(self._load_icon("eye.svg"))

    def _do_register(self):
        invite = self.register_invite.text().strip()
        username = self.register_username.text().strip()
        password = self.register_password.text()
        password2 = self.register_password2.text()
        if not invite or not username or not password:
            self.register_status.setText("Fill all fields.")
            return
        if password != password2:
            self.register_status.setText("Passwords do not match.")
            return
        try:
            user = self.api_client.register(invite, username, password)
            self.register_status.setText("Account created.")
            self.register_invite.clear()
            self.register_username.clear()
            self.register_password.clear()
            self.register_password2.clear()
            self.user = {
                "id": user.get("user_id"),
                "username": user.get("username"),
                "role": user.get("role"),
            }
            self.accept()
        except Exception as exc:
            message = "Registration failed."
            text = str(exc)
            if "Invalid invite code" in text:
                message = "Invite code is invalid."
            elif "Invite exhausted" in text:
                message = "Invite code already used."
            elif "Invite expired" in text:
                message = "Invite code expired."
            elif "Username taken" in text:
                message = "Login already taken."
            elif "Failed to establish a new connection" in text or "Connection refused" in text:
                message = "Server is not reachable."
            elif "ReadTimeout" in text or "timed out" in text:
                message = "Server timeout. Try again."
            self.register_status.setText(message)
            print(f"Registration failed: {exc}")

    def _toggle_register_password(self):
        if self.register_show_pw.isChecked():
            self.register_password.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.register_show_pw.setIcon(self._load_icon("eye-off.svg"))
        else:
            self.register_password.setEchoMode(QtWidgets.QLineEdit.Password)
            self.register_show_pw.setIcon(self._load_icon("eye.svg"))

    def _toggle_register_password2(self):
        if self.register_show_pw2.isChecked():
            self.register_password2.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.register_show_pw2.setIcon(self._load_icon("eye-off.svg"))
        else:
            self.register_password2.setEchoMode(QtWidgets.QLineEdit.Password)
            self.register_show_pw2.setIcon(self._load_icon("eye.svg"))

    def _load_icon(self, name: str) -> QtGui.QIcon:
        from client.resources import resource_path
        path = resource_path("assets", "icons", name)
        if path.exists():
            return QtGui.QIcon(str(path))
        return self.style().standardIcon(QtWidgets.QStyle.SP_DialogHelpButton)
