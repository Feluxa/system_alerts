from PySide6 import QtCore, QtWidgets


class AlertPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = QtWidgets.QLabel("Panic Alert BETA")
        self.title.setObjectName("sectionTitle")
        self.hotkey_label = QtWidgets.QLabel("Hotkey: not set")
        self.hotkey_label.setObjectName("statusLabel")

        self.panic_btn = QtWidgets.QPushButton("PANIC")
        self.panic_btn.setObjectName("panicButton")
        self.panic_btn.setFixedSize(180, 180)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(self.title)
        layout.addWidget(self.hotkey_label)
        layout.addStretch(1)
        layout.addWidget(self.panic_btn, alignment=QtCore.Qt.AlignHCenter)
        layout.addStretch(2)

    def set_hotkey(self, hotkey: str):
        text = hotkey if hotkey else "not set"
        self.hotkey_label.setText(f"Hotkey: {text}")
