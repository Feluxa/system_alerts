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

        code_row = QtWidgets.QHBoxLayout()
        code_row.addWidget(self.code_display)
        code_row.addWidget(self.copy_btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addWidget(self.description)
        layout.addSpacing(10)
        layout.addWidget(self.generate_btn, alignment=QtCore.Qt.AlignLeft)
        layout.addLayout(code_row)
        layout.addStretch(1)

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
