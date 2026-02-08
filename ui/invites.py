from PySide6 import QtCore, QtWidgets


class InvitePage(QtWidgets.QWidget):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api = api_client

        self.title = QtWidgets.QLabel("Invite Codes")
        self.title.setObjectName("sectionTitle")
        self.description = QtWidgets.QLabel(
            "Create one-time invite codes for new users."
        )
        self.description.setObjectName("statusLabel")

        self.generate_btn = QtWidgets.QPushButton("Generate invite")
        self.generate_btn.clicked.connect(self._generate)

        self.code_display = QtWidgets.QLineEdit()
        self.code_display.setReadOnly(True)
        self.code_display.setPlaceholderText("Generated code will appear here")

        self.copy_btn = QtWidgets.QPushButton("Copy")
        self.copy_btn.clicked.connect(self._copy)
        self.version_title = QtWidgets.QLabel("Client Version Policy")
        self.version_title.setObjectName("sectionTitle")
        self.version_desc = QtWidgets.QLabel(
            "Control minimum app version and hard/soft update mode."
        )
        self.version_desc.setObjectName("statusLabel")

        self.min_version = QtWidgets.QLineEdit()
        self.min_version.setPlaceholderText("Minimum client version (e.g., 1.0.0)")
        self.latest_version = QtWidgets.QLineEdit()
        self.latest_version.setPlaceholderText("Latest client version")
        self.download_url = QtWidgets.QLineEdit()
        self.download_url.setPlaceholderText("Download URL")
        self.hard_block = QtWidgets.QCheckBox("Hard block outdated clients")
        self.hard_block.setChecked(True)
        self.version_status = QtWidgets.QLabel("")
        self.version_status.setObjectName("statusLabel")
        self.version_reload_btn = QtWidgets.QPushButton("Load current policy")
        self.version_reload_btn.setObjectName("ghostButton")
        self.version_save_btn = QtWidgets.QPushButton("Save policy")
        self.version_save_btn.setObjectName("primaryButton")
        self.version_reload_btn.clicked.connect(self._load_policy)
        self.version_save_btn.clicked.connect(self._save_policy)

        code_row = QtWidgets.QHBoxLayout()
        code_row.addWidget(self.code_display)
        code_row.addWidget(self.copy_btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addWidget(self.description)
        layout.addSpacing(10)
        layout.addWidget(self.generate_btn, alignment=QtCore.Qt.AlignLeft)
        layout.addLayout(code_row)
        layout.addSpacing(24)
        layout.addWidget(self.version_title)
        layout.addWidget(self.version_desc)
        version_form = QtWidgets.QFormLayout()
        version_form.addRow("Min version", self.min_version)
        version_form.addRow("Latest version", self.latest_version)
        version_form.addRow("Download URL", self.download_url)
        version_form.addRow("", self.hard_block)
        layout.addLayout(version_form)
        version_actions = QtWidgets.QHBoxLayout()
        version_actions.addWidget(self.version_reload_btn)
        version_actions.addWidget(self.version_save_btn)
        version_actions.addStretch(1)
        layout.addLayout(version_actions)
        layout.addWidget(self.version_status)
        layout.addStretch(1)
        self._load_policy()

    def _generate(self):
        try:
            data = self.api.create_invite()
            self.code_display.setText(data.get("code", ""))
        except Exception:
            self.code_display.setText("")

    def _copy(self):
        if not self.code_display.text():
            return
        QtWidgets.QApplication.clipboard().setText(self.code_display.text())

    def _load_policy(self):
        try:
            data = self.api.get_admin_version_policy()
            self.min_version.setText(str(data.get("min_client_version", "")))
            self.latest_version.setText(str(data.get("latest_client_version", "")))
            self.download_url.setText(str(data.get("download_url", "")))
            self.hard_block.setChecked(bool(data.get("hard_block", True)))
            self.version_status.setText("Policy loaded.")
        except Exception:
            self.version_status.setText("Failed to load policy.")

    def _save_policy(self):
        min_version = self.min_version.text().strip()
        latest_version = self.latest_version.text().strip()
        download_url = self.download_url.text().strip()
        if not min_version or not latest_version or not download_url:
            self.version_status.setText("Fill min/latest/download URL.")
            return
        try:
            data = self.api.update_admin_version_policy(
                min_client_version=min_version,
                latest_client_version=latest_version,
                download_url=download_url,
                hard_block=self.hard_block.isChecked(),
            )
            self.min_version.setText(str(data.get("min_client_version", min_version)))
            self.latest_version.setText(str(data.get("latest_client_version", latest_version)))
            self.download_url.setText(str(data.get("download_url", download_url)))
            self.hard_block.setChecked(bool(data.get("hard_block", self.hard_block.isChecked())))
            self.version_status.setText("Policy saved.")
        except Exception:
            self.version_status.setText("Failed to save policy.")
