from PySide6 import QtCore, QtWidgets


class ShortButtonPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = QtWidgets.QLabel("SB")
        self.title.setObjectName("sectionTitle")
        self.title.setAlignment(QtCore.Qt.AlignHCenter)

        self.panic_btn = QtWidgets.QPushButton("ALERT")
        self.panic_btn.setObjectName("panicButton")
        self.panic_btn.setMinimumSize(180, 180)
        self.panic_btn.setMaximumSize(220, 220)

        self.text_input = QtWidgets.QLineEdit()
        self.text_input.setPlaceholderText("Alert text")
        self.send_btn = QtWidgets.QPushButton("Send text")
        self.send_btn.setObjectName("primaryButton")
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(QtCore.Qt.AlignHCenter)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(self.title)
        layout.addStretch(1)
        layout.addWidget(self.panic_btn, alignment=QtCore.Qt.AlignHCenter)
        layout.addWidget(self.text_input)
        layout.addWidget(self.send_btn)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

    def set_status(self, text: str):
        self.status_label.setText(text)
