from PySide6 import QtCore, QtWidgets


class TitleBar(QtWidgets.QWidget):
    def __init__(self, app_name, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(44)
        self._drag_pos = None

        self.title = QtWidgets.QLabel(app_name)
        self.title.setObjectName("appTitle")
        self.user_badge = QtWidgets.QLabel("")
        self.user_badge.setObjectName("badge")
        self.user_badge.hide()

        self.min_btn = QtWidgets.QPushButton("_")
        self.min_btn.setObjectName("titleButton")
        self.min_btn.setToolTip("Minimize")
        self.close_btn = QtWidgets.QPushButton("X")
        self.close_btn.setObjectName("titleButtonClose")
        self.close_btn.setToolTip("Close")

        self.min_btn.clicked.connect(self._on_minimize)
        self.close_btn.clicked.connect(self._on_close)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.addWidget(self.title)
        layout.addStretch(1)
        layout.addSpacing(10)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)

        self._resize_grip = QtWidgets.QSizeGrip(self)
        self._resize_grip.hide()

    def set_role(self, role_text=None):
        # Keep title bar minimal; only update when explicitly needed.
        if role_text:
            self.title.setText(role_text)

    def _on_minimize(self):
        window = self.window()
        if window is not None:
            window.showMinimized()

    def _on_close(self):
        window = self.window()
        if window is not None:
            window.close()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & QtCore.Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            window = self.window()
            if window is not None:
                window.move(window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            window = self.window()
            if window is not None:
                if window.isMaximized():
                    window.showNormal()
                else:
                    window.showMaximized()
        super().mouseDoubleClickEvent(event)
