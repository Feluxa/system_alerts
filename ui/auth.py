from PySide6 import QtCore, QtWidgets


class AuthPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.mode_tabs = QtWidgets.QTabWidget()
        self.login_tab = QtWidgets.QWidget()
        self.register_tab = QtWidgets.QWidget()
        self.mode_tabs.addTab(self.login_tab, "Login")
        self.mode_tabs.addTab(self.register_tab, "Register")

        self._build_login()
        self._build_register()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.mode_tabs)

    def _build_login(self):
        form = QtWidgets.QFormLayout()
        self.login_username = QtWidgets.QLineEdit()
        self.login_password = QtWidgets.QLineEdit()
        self.login_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_btn = QtWidgets.QPushButton("Sign in")
        self.login_status = QtWidgets.QLabel("")
        self.login_status.setObjectName("statusLabel")

        form.addRow("Login", self.login_username)
        form.addRow("Password", self.login_password)

        layout = QtWidgets.QVBoxLayout(self.login_tab)
        layout.addLayout(form)
        layout.addWidget(self.login_btn, alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(self.login_status)
        layout.addStretch(1)

    def _build_register(self):
        form = QtWidgets.QFormLayout()
        self.register_invite = QtWidgets.QLineEdit()
        self.register_username = QtWidgets.QLineEdit()
        self.register_password = QtWidgets.QLineEdit()
        self.register_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.register_password2 = QtWidgets.QLineEdit()
        self.register_password2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.register_btn = QtWidgets.QPushButton("Create account")
        self.register_status = QtWidgets.QLabel("")
        self.register_status.setObjectName("statusLabel")

        form.addRow("Invite code", self.register_invite)
        form.addRow("Login", self.register_username)
        form.addRow("Password", self.register_password)
        form.addRow("Confirm", self.register_password2)

        layout = QtWidgets.QVBoxLayout(self.register_tab)
        layout.addLayout(form)
        layout.addWidget(self.register_btn, alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(self.register_status)
        layout.addStretch(1)
