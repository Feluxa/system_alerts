from PySide6 import QtCore, QtWidgets


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, api_client, app_icon=None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user = None

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
        self.login_btn = QtWidgets.QPushButton("Continue")
        self.login_btn.setObjectName("primaryButton")
        self.login_status = QtWidgets.QLabel("")
        self.login_status.setObjectName("statusLabel")

        self.login_btn.clicked.connect(self._do_login)

        layout = QtWidgets.QVBoxLayout(self.login_tab)
        layout.setSpacing(12)
        layout.addWidget(self.login_username)
        layout.addWidget(self.login_password)
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
        self.register_password2 = QtWidgets.QLineEdit()
        self.register_password2.setPlaceholderText("Confirm password")
        self.register_password2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.register_btn = QtWidgets.QPushButton("Create account")
        self.register_btn.setObjectName("primaryButton")
        self.register_status = QtWidgets.QLabel("")
        self.register_status.setObjectName("statusLabel")

        self.register_btn.clicked.connect(self._do_register)

        layout = QtWidgets.QVBoxLayout(self.register_tab)
        layout.setSpacing(12)
        layout.addWidget(self.register_invite)
        layout.addWidget(self.register_username)
        layout.addWidget(self.register_password)
        layout.addWidget(self.register_password2)
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
        except Exception:
            self.login_status.setText("Invalid login or password.")
            return
        self.user = {
            "id": user.get("user_id"),
            "username": user.get("username"),
            "role": user.get("role"),
        }
        self.accept()

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
            self.register_status.setText("Registration failed.")
