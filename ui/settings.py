import os

from PySide6 import QtCore, QtGui, QtMultimedia, QtWidgets


class SettingsPage(QtWidgets.QWidget):
    theme_changed = QtCore.Signal(str)
    settings_saved = QtCore.Signal(str, str, str, int, bool)
    logout_requested = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.appearance_box = QtWidgets.QGroupBox("Appearance")
        self.theme_select = QtWidgets.QComboBox()
        self.theme_select.addItem("Dark", "dark")
        self.theme_select.addItem("Light", "light")
        self.theme_select.addItem("Neon", "neon")
        self.theme_select.addItem("Pastel", "pastel")
        self.theme_select.currentTextChanged.connect(self._emit_theme)

        appearance_form = QtWidgets.QFormLayout(self.appearance_box)
        appearance_form.addRow("Theme", self.theme_select)
        self.auto_start = QtWidgets.QCheckBox("Run at system startup")
        self.auto_start.stateChanged.connect(lambda _: self._schedule_autosave())
        appearance_form.addRow("Autostart", self.auto_start)

        self.hotkey_box = QtWidgets.QGroupBox("Hotkey")
        self.hotkey = QtWidgets.QLineEdit()
        self.hotkey.setPlaceholderText("Press a key (e.g., Page Up)")
        self.hotkey.setReadOnly(True)
        self.hotkey_capture = QtWidgets.QPushButton("Capture")
        self.hotkey_capture.clicked.connect(self._start_capture)
        self.hotkey_clear = QtWidgets.QPushButton("Clean")
        self.hotkey_clear.clicked.connect(self._clear_hotkey)
        hotkey_row = QtWidgets.QHBoxLayout()
        hotkey_row.addWidget(self.hotkey)
        hotkey_row.addWidget(self.hotkey_capture)
        hotkey_row.addWidget(self.hotkey_clear)
        hotkey_layout = QtWidgets.QVBoxLayout(self.hotkey_box)
        hotkey_layout.addLayout(hotkey_row)

        self.sound_box = QtWidgets.QGroupBox("Sound")
        self.sound_select = QtWidgets.QComboBox()
        self.sound_select.addItems(["Siren", "Alarm", "Beep", "Pulse"])
        self.sound_custom_path = QtWidgets.QLineEdit()
        self.sound_custom_path.setPlaceholderText("Custom sound file (local)")
        self.sound_browse = QtWidgets.QPushButton("Browse")
        self.sound_test = QtWidgets.QPushButton("Test")
        self.sound_browse.clicked.connect(self._browse_sound)
        self.sound_test.clicked.connect(self._test_sound)
        self.sound_select.currentTextChanged.connect(self._schedule_autosave)
        self.sound_custom_path.textChanged.connect(self._schedule_autosave)

        self.volume = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(70)
        self.volume_value = QtWidgets.QLabel("70%")
        self.volume.valueChanged.connect(self._update_volume_label)
        self.volume.valueChanged.connect(lambda _: self._schedule_autosave())

        sound_form = QtWidgets.QFormLayout(self.sound_box)
        sound_row = QtWidgets.QHBoxLayout()
        sound_row.addWidget(self.sound_select)
        sound_row.addWidget(self.sound_test)
        sound_form.addRow("System sound", sound_row)
        custom_row = QtWidgets.QHBoxLayout()
        custom_row.addWidget(self.sound_custom_path)
        custom_row.addWidget(self.sound_browse)
        sound_form.addRow("Custom sound", custom_row)
        volume_row = QtWidgets.QHBoxLayout()
        volume_row.addWidget(self.volume)
        volume_row.addWidget(self.volume_value)
        sound_form.addRow("Volume", volume_row)

        self.save_btn = QtWidgets.QPushButton("Save settings")
        self.logout_btn = QtWidgets.QPushButton("Log out")
        self.logout_btn.setObjectName("ghostButton")
        self.status = QtWidgets.QLabel("")
        self.status.setObjectName("statusLabel")
        self.save_btn.clicked.connect(self._save_settings)
        self.logout_btn.clicked.connect(self.logout_requested.emit)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.appearance_box)
        layout.addWidget(self.hotkey_box)
        layout.addWidget(self.sound_box)
        action_row = QtWidgets.QHBoxLayout()
        action_row.addWidget(self.save_btn)
        action_row.addWidget(self.logout_btn)
        action_row.addStretch(1)
        layout.addLayout(action_row)
        layout.addWidget(self.status)
        layout.addStretch(1)
        self._capture_mode = False

        self._player = QtMultimedia.QMediaPlayer(self)
        self._audio = QtMultimedia.QAudioOutput(self)
        self._player.setAudioOutput(self._audio)

        self._autosave_timer = QtCore.QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.setInterval(400)
        self._autosave_timer.timeout.connect(self._emit_autosave)

    def _update_volume_label(self, value):
        self.volume_value.setText(f"{value}%")

    def set_theme(self, theme):
        index = self.theme_select.findData(theme)
        if index < 0:
            index = self.theme_select.findData("dark")
        self.theme_select.blockSignals(True)
        self.theme_select.setCurrentIndex(index)
        self.theme_select.blockSignals(False)

    def _emit_theme(self, text):
        theme = self.theme_select.currentData() or "dark"
        self.theme_changed.emit(theme)

    def set_settings(self, hotkey, sound_path, system_sound, volume, auto_start=False):
        self.hotkey.setText(hotkey or "")
        self.sound_custom_path.setText(sound_path or "")
        self.set_system_sound(system_sound or "Siren")
        if volume is not None:
            self.volume.setValue(int(volume))
        self.auto_start.setChecked(bool(auto_start))

    def set_system_sound(self, system_sound):
        index = self.sound_select.findText(system_sound)
        if index >= 0:
            self.sound_select.setCurrentIndex(index)

    def _start_capture(self):
        if self._capture_mode:
            return
        self._capture_mode = True
        self.hotkey.setText("Press a key...")
        QtWidgets.QApplication.instance().installEventFilter(self)

    def _stop_capture(self):
        self._capture_mode = False
        QtWidgets.QApplication.instance().removeEventFilter(self)

    def eventFilter(self, watched, event):
        if self._capture_mode and event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            mods = event.modifiers()
            if key in (QtCore.Qt.Key_Control, QtCore.Qt.Key_Shift, QtCore.Qt.Key_Alt, QtCore.Qt.Key_Meta):
                return True
            mods_int = getattr(mods, "value", 0)
            seq = QtGui.QKeySequence(int(mods_int) | key).toString()
            if not seq:
                seq = QtGui.QKeySequence(key).toString()
            self.hotkey.setText(seq)
            self._stop_capture()
            self._schedule_autosave()
            return True
        return super().eventFilter(watched, event)

    def _clear_hotkey(self):
        self.hotkey.setText("")
        self._schedule_autosave()

    def _schedule_autosave(self):
        self._autosave_timer.start()

    def _emit_autosave(self):
        hotkey = self.hotkey.text().strip()
        sound_path = self.sound_custom_path.text().strip()
        system_sound = self.sound_select.currentText()
        volume = self.volume.value()
        auto_start = self.auto_start.isChecked()
        self.settings_saved.emit(hotkey, sound_path, system_sound, volume, auto_start)

    def _browse_sound(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select sound",
            "",
            "Audio files (*.mp3 *.wav *.ogg);;All files (*.*)",
        )
        if path:
            self.sound_custom_path.setText(path)

    def _test_sound(self):
        path = self.sound_custom_path.text().strip()
        if not path:
            name = self.sound_select.currentText()
            system_path = self._resolve_system_sound(name)
            if not system_path:
                self.status.setText("System sound file not found.")
                return
            path = system_path
        if not os.path.exists(path):
            self.status.setText("Select a valid sound file to test.")
            return
        self._player.setSource(QtCore.QUrl.fromLocalFile(path))
        self._audio.setVolume(self.volume.value() / 100.0)
        self._player.play()

    def _save_settings(self):
        hotkey = self.hotkey.text().strip()
        sound_path = self.sound_custom_path.text().strip()
        system_sound = self.sound_select.currentText()
        volume = self.volume.value()
        auto_start = self.auto_start.isChecked()
        self.settings_saved.emit(hotkey, sound_path, system_sound, volume, auto_start)
        self.status.setText("Settings saved.")

    def _resolve_system_sound(self, name):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(base, "assets", "sounds", f"{name.lower()}.wav")
        if os.path.exists(path):
            return path
        path = os.path.join(base, "assets", "sounds", f"{name.lower()}.mp3")
        if os.path.exists(path):
            return path
        path = os.path.join(base, "assets", "sounds", f"{name.lower()}.ogg")
        if os.path.exists(path):
            return path
        return ""
