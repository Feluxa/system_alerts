from PySide6 import QtCore, QtWidgets


class TeamsPage(QtWidgets.QWidget):
    team_changed = QtCore.Signal(int)
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api = api_client
        self.current_user = None
        self.current_team = None
        self.current_team_role = None

        self.team_title = QtWidgets.QLabel("Team:")
        self.team_title.setObjectName("sectionTitle")
        self.team_name_label = QtWidgets.QLabel("No team")
        self.team_name_label.setObjectName("teamName")
        self.team_desc_label = QtWidgets.QLabel("")
        self.team_desc_label.setObjectName("statusLabel")

        self.no_team_panel = QtWidgets.QWidget()
        self.join_team_btn = QtWidgets.QPushButton("Join a team")
        self.join_team_btn.setObjectName("primaryOutlineButton")
        self.join_team_btn.setMinimumHeight(48)
        self.join_team_btn.setMinimumWidth(260)
        self.create_team_btn = QtWidgets.QPushButton("Create a team")
        self.create_team_btn.setObjectName("primaryOutlineButton")
        self.create_team_btn.setMinimumHeight(48)
        self.create_team_btn.setMinimumWidth(260)
        self.join_team_btn.clicked.connect(self._open_join_dialog)
        self.create_team_btn.clicked.connect(self._open_create_dialog)
        self.no_team_status = QtWidgets.QLabel("")
        self.no_team_status.setObjectName("statusLabel")

        self.invite_code = QtWidgets.QLineEdit()
        self.invite_code.setReadOnly(True)
        self.invite_code.setPlaceholderText("Invite code")
        self.generate_invite_btn = QtWidgets.QPushButton("Generate invite")
        self.generate_invite_btn.clicked.connect(self._generate_team_invite)

        self.invite_toggle = QtWidgets.QToolButton()
        self.invite_toggle.setCheckable(True)
        self.invite_toggle.setChecked(False)
        self.invite_toggle.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.invite_toggle.setArrowType(QtCore.Qt.RightArrow)
        self.invite_toggle.setText("Invite code")
        self.invite_toggle.clicked.connect(self._toggle_invite_box)
        self.leave_btn = QtWidgets.QPushButton("Leave team")
        self.leave_btn.setObjectName("dangerButton")
        self.leave_btn.clicked.connect(self._leave_team)
        self.edit_team_btn = QtWidgets.QPushButton("Edit team")
        self.edit_team_btn.setObjectName("ghostButton")
        self.edit_team_btn.clicked.connect(self._open_edit_dialog)

        self.telegram_box = QtWidgets.QGroupBox("Telegram Alerts")
        self.telegram_chat_id = QtWidgets.QLineEdit()
        self.telegram_chat_id.setPlaceholderText("Chat ID (e.g., -1001234567890)")
        self.telegram_bot_token = QtWidgets.QLineEdit()
        self.telegram_bot_token.setPlaceholderText("Bot token from BotFather")
        self.telegram_bot_token.setEchoMode(QtWidgets.QLineEdit.Password)
        self.telegram_save_btn = QtWidgets.QPushButton("Save Telegram")
        self.telegram_save_btn.setObjectName("primaryButton")
        self.telegram_test_btn = QtWidgets.QPushButton("Test alert")
        self.telegram_test_btn.setObjectName("ghostButton")
        self.telegram_test_btn.clicked.connect(self._test_telegram)
        self.telegram_status = QtWidgets.QLabel("")
        self.telegram_status.setObjectName("statusLabel")
        self.telegram_save_btn.clicked.connect(self._save_telegram)
        self.telegram_guide_btn = QtWidgets.QPushButton("How to connect Telegram")
        self.telegram_guide_btn.setObjectName("ghostButton")
        self.telegram_guide_btn.clicked.connect(self._show_telegram_guide)

        self.telegram_toggle = QtWidgets.QToolButton()
        self.telegram_toggle.setCheckable(True)
        self.telegram_toggle.setChecked(False)
        self.telegram_toggle.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.telegram_toggle.setArrowType(QtCore.Qt.RightArrow)
        self.telegram_toggle.setText("Telegram alerts")
        self.telegram_toggle.clicked.connect(self._toggle_telegram_box)

        telegram_form = QtWidgets.QFormLayout(self.telegram_box)
        telegram_form.addRow("Chat ID", self.telegram_chat_id)
        telegram_form.addRow("Bot token", self.telegram_bot_token)
        telegram_form.addRow(self.telegram_save_btn)
        telegram_form.addRow(self.telegram_test_btn)
        telegram_form.addRow(self.telegram_guide_btn)
        telegram_form.addRow(self.telegram_status)

        self.members_title = QtWidgets.QLabel("Members")
        self.members_title.setObjectName("sectionTitle")
        self.members_table = QtWidgets.QTableWidget(0, 3)
        self.members_table.setHorizontalHeaderLabels(["Login", "Role", "Actions"])
        self.members_table.horizontalHeader().setStretchLastSection(True)
        self.members_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.members_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.members_status = QtWidgets.QLabel("")
        self.members_status.setObjectName("statusLabel")

        no_team_layout = QtWidgets.QVBoxLayout(self.no_team_panel)
        no_team_layout.setSpacing(12)
        no_team_layout.addStretch(1)
        no_team_layout.addWidget(self.join_team_btn, alignment=QtCore.Qt.AlignLeft)
        no_team_layout.addWidget(self.create_team_btn, alignment=QtCore.Qt.AlignLeft)
        no_team_layout.addWidget(self.no_team_status)
        no_team_layout.addStretch(2)

        header_row = QtWidgets.QHBoxLayout()
        header_row.addWidget(self.team_title)
        header_row.addStretch(1)
        header_row.addWidget(self.edit_team_btn)
        header_row.addWidget(self.leave_btn)

        invite_row = QtWidgets.QHBoxLayout()
        invite_row.addWidget(self.invite_code)
        invite_row.addWidget(self.generate_invite_btn)

        self.invite_row_container = QtWidgets.QWidget()
        self.invite_row_container.setLayout(invite_row)

        self.team_panel = QtWidgets.QWidget()
        team_layout = QtWidgets.QVBoxLayout(self.team_panel)
        team_layout.addLayout(header_row)
        team_layout.addWidget(self.team_name_label)
        team_layout.addWidget(self.team_desc_label)
        team_layout.addSpacing(8)
        team_layout.addWidget(self.invite_toggle, alignment=QtCore.Qt.AlignLeft)
        team_layout.addWidget(self.invite_row_container)
        team_layout.addSpacing(8)
        team_layout.addWidget(self.telegram_toggle, alignment=QtCore.Qt.AlignLeft)
        team_layout.addWidget(self.telegram_box)
        team_layout.addSpacing(8)
        team_layout.addWidget(self.members_title)
        team_layout.addWidget(self.members_table)
        team_layout.addWidget(self.members_status)

        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self.no_team_panel)
        self.stack.addWidget(self.team_panel)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.stack)

        self._set_team_controls_enabled(False)

    def set_current_user(self, user):
        self.current_user = user
        self.refresh_teams()

    def refresh_teams(self):
        self.current_team = None
        self.current_team_role = None
        if not self.current_user:
            self._set_team_controls_enabled(False)
            self.stack.setCurrentWidget(self.no_team_panel)
            self.team_changed.emit(0)
            return
        try:
            team = self.api.my_team()
        except Exception:
            team = None
        if not team:
            self._set_team_controls_enabled(False)
            self.stack.setCurrentWidget(self.no_team_panel)
            self._render_members([])
            self.team_changed.emit(0)
            return
        self.current_team = team
        self.current_team_role = team.get("role", "user")
        self.telegram_chat_id.setText(team.get("telegram_chat_id") or "")
        try:
            members = self.api.list_members(self.current_team["id"])
        except Exception:
            members = []
        self._render_members(members)
        self._set_team_controls_enabled(True)
        self._set_team_header()
        self.stack.setCurrentWidget(self.team_panel)
        self.team_changed.emit(self.current_team["id"])

    def _set_team_controls_enabled(self, enabled):
        can_manage = enabled and self._can_manage_team()
        self.invite_toggle.setVisible(can_manage)
        self.invite_row_container.setVisible(can_manage and self.invite_toggle.isChecked())
        self.members_table.setEnabled(enabled)
        self.generate_invite_btn.setEnabled(can_manage)
        self.invite_code.setEnabled(can_manage)
        self.leave_btn.setEnabled(enabled)
        self.telegram_toggle.setVisible(can_manage)
        self.telegram_box.setVisible(can_manage and self.telegram_toggle.isChecked())
        self.edit_team_btn.setVisible(can_manage)

    def _can_manage_team(self):
        if not self.current_user or not self.current_team_role:
            return False
        if self.current_user["role"] == "super_admin":
            return True
        return self.current_team_role in ("owner", "admin")

    def _render_members(self, members):
        self.members_table.setRowCount(len(members))
        for row, member in enumerate(members):
            self.members_table.setItem(row, 0, QtWidgets.QTableWidgetItem(member["username"]))
            self.members_table.setItem(row, 1, QtWidgets.QTableWidgetItem(member["role"]))
            if self._can_manage_team():
                action_widget = QtWidgets.QWidget()
                actions = QtWidgets.QHBoxLayout(action_widget)
                actions.setContentsMargins(0, 0, 0, 0)
                if not self.current_user or member["user_id"] != self.current_user.get("id"):
                    remove = QtWidgets.QPushButton("Remove")
                    remove.setProperty("compact", True)
                    remove.clicked.connect(
                        lambda _, uid=member["user_id"]: self._remove_member(uid)
                    )
                    actions.addWidget(remove)
                actions.addStretch(1)
                self.members_table.setCellWidget(row, 2, action_widget)
            else:
                self.members_table.setCellWidget(row, 2, QtWidgets.QWidget())

    def apply_member_update(self, members):
        if not self.current_user:
            return
        user_id = self.current_user.get("id")
        in_team = any(m["user_id"] == user_id for m in members)
        if not in_team:
            self.current_team = None
            self.current_team_role = None
            self._set_team_controls_enabled(False)
            self._render_members([])
            self.stack.setCurrentWidget(self.no_team_panel)
            self.team_changed.emit(0)
            return
        # Update role for current user
        for m in members:
            if m["user_id"] == user_id:
                self.current_team_role = m["role"]
                break
        self._render_members(members)
        self._set_team_controls_enabled(True)

    def apply_team_update(self, team_info: dict | None, members: list | None = None):
        if not self.current_team or not team_info:
            return
        if "name" in team_info:
            self.current_team["name"] = team_info.get("name", self.current_team.get("name"))
        if "description" in team_info:
            self.current_team["description"] = team_info.get("description")
        self._set_team_header()
        if isinstance(members, list):
            self.apply_member_update(members)

    def _open_create_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        dialog.setFixedSize(360, 240)
        dialog.setObjectName("confirmDialog")
        title = QtWidgets.QLabel("Create team")
        title.setObjectName("sectionTitle")
        close_btn = QtWidgets.QPushButton("X")
        close_btn.setObjectName("titleButtonClose")
        close_btn.setFixedSize(28, 24)
        close_btn.clicked.connect(dialog.reject)
        name = QtWidgets.QLineEdit()
        name.setPlaceholderText("Team name")
        desc = QtWidgets.QLineEdit()
        desc.setPlaceholderText("Description")
        status = QtWidgets.QLabel("")
        status.setObjectName("statusLabel")
        submit = QtWidgets.QPushButton("Create")
        submit.setObjectName("primaryButton")

        def _submit():
            if not self.current_user:
                return
            value = name.text().strip()
            if not value:
                status.setText("Enter team name.")
                return
            try:
                self.api.create_team(value, desc.text().strip())
                status.setText("Team created.")
                dialog.accept()
            except Exception:
                status.setText("Failed to create team.")

        submit.clicked.connect(_submit)

        frame = QtWidgets.QFrame()
        frame.setObjectName("confirmFrame")
        frame_layout = QtWidgets.QVBoxLayout(frame)
        frame_layout.setContentsMargins(16, 16, 16, 16)
        frame_layout.setSpacing(12)
        header = QtWidgets.QHBoxLayout()
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(close_btn)
        frame_layout.addLayout(header)
        frame_layout.addWidget(name)
        frame_layout.addWidget(desc)
        frame_layout.addWidget(submit)
        frame_layout.addWidget(status)

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(frame)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.refresh_teams()

    def _open_join_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        dialog.setFixedSize(360, 220)
        dialog.setObjectName("confirmDialog")
        title = QtWidgets.QLabel("Join team")
        title.setObjectName("sectionTitle")
        close_btn = QtWidgets.QPushButton("X")
        close_btn.setObjectName("titleButtonClose")
        close_btn.setFixedSize(28, 24)
        close_btn.clicked.connect(dialog.reject)
        invite = QtWidgets.QLineEdit()
        invite.setPlaceholderText("Invite link/code")
        status = QtWidgets.QLabel("")
        status.setObjectName("statusLabel")
        submit = QtWidgets.QPushButton("Join")
        submit.setObjectName("primaryButton")

        def _submit():
            if not self.current_user:
                return
            code = invite.text().strip()
            if not code:
                status.setText("Enter invite code.")
                return
            try:
                self.api.join_team(code)
                status.setText("Joined team.")
                dialog.accept()
            except Exception:
                status.setText("Failed to join team.")

        submit.clicked.connect(_submit)

        frame = QtWidgets.QFrame()
        frame.setObjectName("confirmFrame")
        frame_layout = QtWidgets.QVBoxLayout(frame)
        frame_layout.setContentsMargins(16, 16, 16, 16)
        frame_layout.setSpacing(12)
        header = QtWidgets.QHBoxLayout()
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(close_btn)
        frame_layout.addLayout(header)
        frame_layout.addWidget(invite)
        frame_layout.addWidget(submit)
        frame_layout.addWidget(status)

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(frame)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.refresh_teams()

    def _open_edit_dialog(self):
        if not self.current_team or not self._can_manage_team():
            return
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        dialog.setFixedSize(360, 240)
        dialog.setObjectName("confirmDialog")
        title = QtWidgets.QLabel("Edit team")
        title.setObjectName("sectionTitle")
        close_btn = QtWidgets.QPushButton("X")
        close_btn.setObjectName("titleButtonClose")
        close_btn.setFixedSize(28, 24)
        close_btn.clicked.connect(dialog.reject)
        name = QtWidgets.QLineEdit()
        name.setPlaceholderText("Team name")
        name.setText(self.current_team.get("name", ""))
        desc = QtWidgets.QLineEdit()
        desc.setPlaceholderText("Description")
        desc.setText(self.current_team.get("description") or "")
        status = QtWidgets.QLabel("")
        status.setObjectName("statusLabel")
        submit = QtWidgets.QPushButton("Save")
        submit.setObjectName("primaryButton")

        def _submit():
            value = name.text().strip()
            if not value:
                status.setText("Enter team name.")
                return
            try:
                data = self.api.update_team(self.current_team["id"], value, desc.text().strip())
                self.current_team.update(
                    {"name": data.get("name", value), "description": data.get("description")}
                )
                self._set_team_header()
                status.setText("Team updated.")
                dialog.accept()
            except Exception:
                status.setText("Failed to update team.")

        submit.clicked.connect(_submit)

        frame = QtWidgets.QFrame()
        frame.setObjectName("confirmFrame")
        frame_layout = QtWidgets.QVBoxLayout(frame)
        frame_layout.setContentsMargins(16, 16, 16, 16)
        frame_layout.setSpacing(12)
        header = QtWidgets.QHBoxLayout()
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(close_btn)
        frame_layout.addLayout(header)
        frame_layout.addWidget(name)
        frame_layout.addWidget(desc)
        frame_layout.addWidget(submit)
        frame_layout.addWidget(status)

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(frame)
        dialog.exec()

    def _generate_team_invite(self):
        if not self.current_team:
            return
        if not self._can_manage_team():
            return
        try:
            data = self.api.rotate_invite(self.current_team["id"])
            self.invite_code.setText(data.get("join_code", ""))
        except Exception:
            self.invite_code.setText("")

    def _leave_team(self):
        if not self.current_team or not self.current_user:
            return
        confirm = QtWidgets.QDialog(self)
        confirm.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        confirm.setFixedSize(320, 160)
        confirm.setObjectName("confirmDialog")

        title = QtWidgets.QLabel("Leave team")
        title.setObjectName("sectionTitle")
        text = QtWidgets.QLabel("Are you sure you want to leave the team?")
        text.setWordWrap(True)
        text.setObjectName("statusLabel")

        yes_btn = QtWidgets.QPushButton("Yes")
        yes_btn.setObjectName("dangerButton")
        no_btn = QtWidgets.QPushButton("No")
        no_btn.setObjectName("ghostButton")
        yes_btn.clicked.connect(confirm.accept)
        no_btn.clicked.connect(confirm.reject)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(no_btn)
        btn_row.addWidget(yes_btn)

        frame = QtWidgets.QFrame()
        frame.setObjectName("confirmFrame")
        frame_layout = QtWidgets.QVBoxLayout(frame)
        frame_layout.setContentsMargins(16, 16, 16, 16)
        frame_layout.setSpacing(10)
        frame_layout.addWidget(title)
        frame_layout.addWidget(text)
        frame_layout.addStretch(1)
        frame_layout.addLayout(btn_row)

        layout = QtWidgets.QVBoxLayout(confirm)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(frame)

        if confirm.exec() != QtWidgets.QDialog.Accepted:
            return
        try:
            self.api.leave_team(self.current_team["id"])
        except Exception:
            return
        self.invite_code.clear()
        self._render_members([])
        self._set_team_controls_enabled(False)
        self.stack.setCurrentWidget(self.no_team_panel)
        self.refresh_teams()

    def _remove_member(self, user_id):
        if not self.current_team:
            return
        if not self._can_manage_team():
            return
        if self.current_user and user_id == self.current_user["id"]:
            return
        try:
            self.api.remove_member(self.current_team["id"], user_id)
        except Exception:
            self.members_status.setText("Failed to remove member (check server).")
            return
        try:
            members = self.api.list_members(self.current_team["id"])
        except Exception:
            members = []
        self.members_status.setText("Member removed.")
        self._render_members(members)

    def _set_team_header(self):
        if not self.current_team:
            self.team_name_label.setText("No team")
            self.team_desc_label.setText("")
            return
        self.team_name_label.setText(self.current_team["name"])
        self.team_desc_label.setText(self.current_team.get("description") or "")

    def _save_telegram(self):
        if not self.current_team:
            return
        chat_id = self.telegram_chat_id.text().strip()
        token = self.telegram_bot_token.text().strip()
        if not chat_id or not token:
            self.telegram_status.setText("Enter chat ID and bot token.")
            return
        try:
            self.api.set_team_telegram(self.current_team["id"], chat_id, token)
            self.telegram_status.setText("Telegram settings saved.")
        except Exception:
            self.telegram_status.setText("Failed to save Telegram settings.")

    def _toggle_telegram_box(self):
        if not self._can_manage_team():
            self.telegram_toggle.setChecked(False)
            self.telegram_box.setVisible(False)
            return
        is_open = self.telegram_toggle.isChecked()
        self.telegram_box.setVisible(is_open)
        self.telegram_toggle.setArrowType(
            QtCore.Qt.DownArrow if is_open else QtCore.Qt.RightArrow
        )

    def _toggle_invite_box(self):
        if not self._can_manage_team():
            self.invite_toggle.setChecked(False)
            self.invite_row_container.setVisible(False)
            return
        is_open = self.invite_toggle.isChecked()
        self.invite_row_container.setVisible(is_open)
        self.invite_toggle.setArrowType(
            QtCore.Qt.DownArrow if is_open else QtCore.Qt.RightArrow
        )

    def _test_telegram(self):
        if not self.current_team:
            return
        try:
            self.api.test_telegram(self.current_team["id"])
            self.telegram_status.setText("Test sent.")
        except Exception:
            self.telegram_status.setText("Test failed.")

    def _show_telegram_guide(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Telegram Setup Guide")
        dialog.setFixedSize(460, 360)
        dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        dialog.setObjectName("confirmDialog")

        title = QtWidgets.QLabel("How to connect Telegram alerts")
        title.setObjectName("sectionTitle")
        text = QtWidgets.QLabel(
            "1) Open Telegram and create a bot in @BotFather. Copy the BOT TOKEN.\n"
            "2) Create a team group and add the bot to the group.\n"
            "3) Make the bot an admin.\n"
            "4) Open this link in your browser:"
        )
        text.setWordWrap(True)
        text.setObjectName("statusLabel")

        url_field = QtWidgets.QLineEdit("https://api.telegram.org/botBOT_TOKEN_HERE/getUpdates")
        url_field.setReadOnly(True)
        copy_btn = QtWidgets.QPushButton("Copy link")
        copy_btn.setObjectName("ghostButton")
        copy_btn.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(url_field.text()))

        url_row = QtWidgets.QHBoxLayout()
        url_row.addWidget(url_field)
        url_row.addWidget(copy_btn)

        text2 = QtWidgets.QLabel("5) Paste Chat ID and BOT TOKEN here and click Save.")
        text2.setWordWrap(True)
        text2.setObjectName("statusLabel")

        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setObjectName("ghostButton")
        close_btn.clicked.connect(dialog.reject)

        frame = QtWidgets.QFrame()
        frame.setObjectName("confirmFrame")
        frame_layout = QtWidgets.QVBoxLayout(frame)
        frame_layout.setContentsMargins(16, 16, 16, 16)
        frame_layout.setSpacing(10)
        frame_layout.addWidget(title)
        frame_layout.addWidget(text)
        frame_layout.addLayout(url_row)
        frame_layout.addWidget(text2)
        frame_layout.addStretch(1)
        frame_layout.addWidget(close_btn, alignment=QtCore.Qt.AlignRight)

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(frame)

        dialog.exec()
