from PySide6 import QtCore, QtWidgets


class AlertPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = QtWidgets.QLabel("Panic Alert  2.0")
        self.title.setObjectName("sectionTitle")
        self.hotkey_label = QtWidgets.QLabel("Hotkey: not set")
        self.hotkey_label.setObjectName("statusLabel")
        self.ws_label = QtWidgets.QLabel("WS: disconnected")
        self.ws_label.setObjectName("statusLabel")

        self.panic_btn = QtWidgets.QPushButton("PANIC")
        self.panic_btn.setObjectName("panicButton")
        self.panic_btn.setFixedSize(180, 180)
        self.text_input = QtWidgets.QLineEdit()
        self.text_input.setPlaceholderText("Alert text (optional)")
        self.text_input.setFixedWidth(360)
        self.send_btn = QtWidgets.QPushButton("Send alert")
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setObjectName("statusLabel")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(self.title)
        layout.addWidget(self.hotkey_label)
        layout.addWidget(self.ws_label)
        layout.addStretch(1)
        layout.addWidget(self.panic_btn, alignment=QtCore.Qt.AlignHCenter)
        layout.addSpacing(8)
        form_row = QtWidgets.QHBoxLayout()
        form_row.addStretch(1)
        form_row.addWidget(self.text_input)
        form_row.addWidget(self.send_btn)
        form_row.addStretch(1)
        layout.addLayout(form_row)
        layout.addWidget(self.status_label, alignment=QtCore.Qt.AlignHCenter)
        layout.addStretch(2)

    def set_hotkey(self, hotkey: str):
        text = hotkey if hotkey else "not set"
        self.hotkey_label.setText(f"Hotkey: {text}")

    def set_ws_status(self, connected: bool):
        self.ws_label.setText("WS: connected" if connected else "WS: disconnected")

    def set_status(self, text: str):
        self.status_label.setText(text)
