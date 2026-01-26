from PySide6 import QtCore, QtGui, QtWidgets


class Sidebar(QtWidgets.QFrame):
    nav_changed = QtCore.Signal(str)
    account_requested = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._expanded = True
        self._buttons = {}
        self._active_key = None
        self._anim = None
        self._anim_max = None
        self._expanded_width = 220
        self._collapsed_width = 72

        self.toggle_btn = QtWidgets.QToolButton()
        self.toggle_btn.setObjectName("sidebarToggle")
        self.toggle_btn.setText("≡")
        self.toggle_btn.setToolTip("Close sidebar")
        self.toggle_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self._toggle)

        self.nav_container = QtWidgets.QVBoxLayout()
        self.nav_container.setSpacing(6)
        self.nav_container.addStretch(1)

        self.profile_card = QtWidgets.QFrame()
        self.profile_card.setObjectName("profileCard")
        self.profile_card.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.avatar = QtWidgets.QPushButton("U")
        self.avatar.setObjectName("avatarButton")
        self.avatar.setCursor(QtCore.Qt.PointingHandCursor)
        self.avatar.clicked.connect(self.account_requested.emit)
        self.profile_name = QtWidgets.QLabel("")
        self.profile_name.setObjectName("profileName")
        self.account_label = QtWidgets.QLabel("Account")
        self.account_label.setObjectName("profileRole")
        self.account_label.hide()

        self.profile_layout = QtWidgets.QVBoxLayout(self.profile_card)
        self.profile_layout.setContentsMargins(10, 10, 10, 10)
        self.profile_layout.setSpacing(6)
        self.profile_layout.addWidget(self.avatar, alignment=QtCore.Qt.AlignLeft)
        self.profile_layout.addWidget(self.account_label, alignment=QtCore.Qt.AlignLeft)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 12)
        layout.setSpacing(12)
        layout.addWidget(self.toggle_btn, alignment=QtCore.Qt.AlignLeft)
        layout.addLayout(self.nav_container)
        layout.addWidget(self.profile_card)
        self._layout = layout

        self._apply_size()

    def set_items(self, items):
        for btn in self._buttons.values():
            self.nav_container.removeWidget(btn)
            btn.deleteLater()
        self._buttons.clear()

        for key, label in items:
            btn = QtWidgets.QPushButton(label)
            btn.setCheckable(True)
            btn.setObjectName("navButton")
            btn.setProperty("navKey", key)
            btn.setProperty("navLabel", label)
            btn.setProperty("collapsed", False)
            btn.clicked.connect(lambda _, k=key: self.nav_changed.emit(k))
            self._buttons[key] = btn
            self.nav_container.insertWidget(self.nav_container.count() - 1, btn)

        if items:
            self.set_active(items[0][0])
        self._apply_size()

    def set_active(self, key):
        self._active_key = key
        for btn_key, btn in self._buttons.items():
            btn.setChecked(btn_key == key)

    def set_profile(self, username, role):
        self.profile_name.setText(username)
        self.avatar.setText(username[:1].upper() if username else "U")
        self.profile_name.hide()
        self.avatar.setToolTip("Account")
        self.account_label.setText("Account")

    def _toggle(self):
        self._expanded = not self._expanded
        self._prepare_state(not self._expanded)
        self._animate_size()

    def _apply_size(self):
        if self._expanded:
            self.setFixedWidth(self._expanded_width)
            self.toggle_btn.setToolTip("Close sidebar")
            for btn in self._buttons.values():
                btn.setToolTip("")
                btn.setProperty("collapsed", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            self._layout.setAlignment(self.toggle_btn, QtCore.Qt.AlignLeft)
            self.profile_layout.setContentsMargins(10, 10, 10, 10)
            self.profile_layout.setAlignment(self.avatar, QtCore.Qt.AlignLeft)
            self.account_label.show()
            self.profile_card.setFixedHeight(86)
        else:
            self.setFixedWidth(self._collapsed_width)
            self.toggle_btn.setToolTip("Open sidebar")
            for key, btn in self._buttons.items():
                btn.setToolTip(btn.property("navLabel"))
                btn.setProperty("collapsed", True)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            self._layout.setAlignment(self.toggle_btn, QtCore.Qt.AlignHCenter)
            self.profile_layout.setContentsMargins(6, 6, 6, 6)
            self.profile_layout.setAlignment(self.avatar, QtCore.Qt.AlignHCenter)
            self.account_label.hide()
            self.profile_card.setFixedHeight(72)

    def _prepare_state(self, collapsing):
        if collapsing:
            for key, btn in self._buttons.items():
                label = btn.property("navLabel") or ""
                btn.setText(label[:1].upper())
                btn.setToolTip(btn.property("navLabel"))
                btn.setProperty("collapsed", True)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
        else:
            for btn in self._buttons.values():
                btn.setText(btn.property("navLabel"))
                btn.setToolTip("")
                btn.setProperty("collapsed", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    def _animate_size(self):
        target = self._expanded_width if self._expanded else self._collapsed_width
        start = self.width()
        if self._anim is not None:
            self._anim.stop()
        if self._anim_max is not None:
            self._anim_max.stop()
        self._anim = QtCore.QPropertyAnimation(self, b"minimumWidth")
        self._anim_max = QtCore.QPropertyAnimation(self, b"maximumWidth")
        self._anim.setDuration(100)
        self._anim_max.setDuration(100)
        self._anim.setStartValue(start)
        self._anim.setEndValue(target)
        self._anim_max.setStartValue(start)
        self._anim_max.setEndValue(target)
        self._anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self._anim_max.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self._anim.finished.connect(self._apply_size)
        self._anim.start()
        self._anim_max.start()

    def _load_profile_photo(self):
        return False
