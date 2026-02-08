from PySide6 import QtGui, QtWidgets


def apply_theme(app: QtWidgets.QApplication, theme: str):
    theme = theme if theme in ("dark", "light", "neon", "pastel") else "dark"
    app.setProperty("theme", theme)
    app.setStyle("Fusion")
    if theme == "light":
        _apply_light(app)
    elif theme == "neon":
        _apply_neon(app)
    elif theme == "pastel":
        _apply_pastel(app)
    else:
        _apply_dark(app)


def _apply_dark(app: QtWidgets.QApplication):
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#1f1f1f"))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#f8fafc"))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor("#2a2a2a"))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#2f2f2f"))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor("#f8fafc"))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor("#2a2a2a"))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#f8fafc"))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#19c37d"))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#0b1220"))
    app.setPalette(palette)

    app.setStyleSheet(
        """
        QWidget {
            font-size: 13px;
            font-family: "Inter", "Segoe UI", "SF Pro Text", "Arial";
            color: #f8fafc;
        }
        QMainWindow {
            background-color: #1f1f1f;
        }
        QDialog#loginDialog {
            border: 1px solid #000000;
            border-radius: 12px;
        }
        QDialog#loginDialog {
            background: #1f1f1f;
        }
        QFrame#loginFrame {
            background: #1f1f1f;
            border: 1px solid #000000;
            border-radius: 12px;
        }
        QFrame#windowFrame {
            background: #1f1f1f;
            border: 1px solid #000000;
            border-radius: 12px;
        }
        QDialog#confirmDialog {
            background: #1f1f1f;
            border: 1px solid #000000;
            border-radius: 12px;
        }
        QFrame#confirmFrame {
            background: #1f1f1f;
            border: 1px solid #2f2f2f;
            border-radius: 12px;
        }
        QWidget#titleBar {
            background: #1f1f1f;
            border-bottom: 1px solid #2f2f2f;
        }
        QLabel#loginTitle {
            font-size: 20px;
            font-weight: 600;
        }
        QLabel#loginSubtitle {
            color: #a1a1aa;
        }
        QTabWidget::pane {
            border: none;
        }
        QTabBar::tab {
            background: transparent;
            color: #a1a1aa;
            padding: 6px 12px;
        }
        QTabBar::tab:selected {
            color: #f8fafc;
            border-bottom: 2px solid #19c37d;
        }
        QFrame#sidebar {
            background: #1c1c1c;
            border: 1px solid #2a2a2a;
            border-radius: 16px;
        }
        QPushButton#navButton {
            text-align: left;
            padding: 10px 12px;
            border-radius: 10px;
            background: transparent;
            border: 1px solid transparent;
        }
        QPushButton#navButton[collapsed="true"] {
            text-align: center;
            padding: 10px 0;
        }
        QPushButton#navButton:checked {
            background: #2a2a2a;
            border: 1px solid #2f2f2f;
        }
        QToolButton#sidebarToggle {
            background: #2a2a2a;
            border: 1px solid #2f2f2f;
            border-radius: 10px;
            padding: 6px 8px;
        }
        QToolButton#sidebarToggle:hover {
            background: #333333;
        }
        QFrame#profileCard {
            background: #222222;
            border: 1px solid #2f2f2f;
            border-radius: 14px;
        }
        QPushButton#avatarButton {
            background: #2f2f2f;
            border: 1px solid #3a3a3a;
            border-radius: 16px;
            min-width: 32px;
            min-height: 32px;
            max-width: 32px;
            max-height: 32px;
            padding: 0;
            color: #f8fafc;
        }
        QPushButton#avatarButton:hover {
            background: #3a3a3a;
        }
        QLabel#profileName {
            font-weight: 600;
        }
        QLabel#profileRole {
            color: #a1a1aa;
        }
        QPushButton#ghostButton {
            background: transparent;
            border: 1px solid #2f2f2f;
            color: #f8fafc;
        }
        QPushButton#ghostButton:hover {
            background: #2a2a2a;
        }
        QPushButton#dangerButton {
            background: #3b2020;
            border: 1px solid #553030;
            color: #fecaca;
        }
        QPushButton#dangerButton:hover {
            background: #4a2525;
        }
        QPushButton#panicButton {
            background: #7f1d1d;
            border: 1px solid #991b1b;
            color: #fecaca;
            font-size: 16px;
            font-weight: 700;
            padding: 14px 20px;
            border-radius: 90px;
        }
        QPushButton#panicButton:hover {
            background: #991b1b;
        }
        QPushButton#primaryButton {
            background: #19c37d;
            border: 1px solid #19c37d;
            color: #0b1220;
        }
        QPushButton#primaryButton:hover {
            background: #16a36a;
        }
        QPushButton#primaryOutlineButton {
            background: transparent;
            border: 2px solid #19c37d;
            color: #19c37d;
            font-size: 14px;
            font-weight: 600;
        }
        QPushButton#primaryOutlineButton:hover {
            background: #1f2a24;
        }
        QListWidget {
            background: #1f1f1f;
            border: 1px solid #2f2f2f;
            border-radius: 14px;
            padding: 8px;
        }
        QListWidget::item {
            padding: 10px 12px;
            border-radius: 10px;
            color: #f8fafc;
        }
        QListWidget::item:selected {
            background: #343434;
            color: #ffffff;
        }
        QPushButton {
            padding: 8px 14px;
            border-radius: 10px;
            background: #343434;
            color: #ffffff;
            border: 1px solid #3a3a3a;
        }
        QPushButton:hover {
            background: #3c3c3c;
        }
        QPushButton:pressed {
            background: #2a2a2a;
        }
        QPushButton[active="true"] {
            background: #19c37d;
            border: 1px solid #19c37d;
            color: #0b1220;
        }
        QPushButton#titleButton, QPushButton#titleButtonClose {
            min-width: 28px;
            max-width: 28px;
            min-height: 24px;
            max-height: 24px;
            padding: 0;
            border-radius: 6px;
            background: #2a2a2a;
            color: #f8fafc;
            border: 1px solid #3a3a3a;
        }
        QPushButton#titleButtonClose {
            background: #3b2020;
            border: 1px solid #553030;
            color: #fecaca;
        }
        QPushButton#titleButtonClose:hover {
            background: #4a2525;
        }
        QPushButton[compact="true"] {
            padding: 4px 8px;
            font-size: 12px;
        }
        QLineEdit, QComboBox, QTableWidget, QTabWidget::pane, QSlider, QGroupBox {
            background: #242424;
            border: 1px solid #2f2f2f;
            border-radius: 12px;
            padding: 8px;
            color: #f8fafc;
        }
        QGroupBox::title {
            color: #a1a1aa;
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
        }
        QHeaderView::section {
            background: #262626;
            border: 1px solid #2f2f2f;
            padding: 8px;
            color: #f8fafc;
        }
        QLabel#appTitle {
            font-size: 18px;
            font-weight: 600;
            color: #f8fafc;
        }
        QLabel#sectionTitle {
            font-size: 14px;
            font-weight: 600;
            color: #f8fafc;
        }
        QLabel#badge {
            background: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 10px;
            padding: 6px 10px;
            color: #f8fafc;
        }
        QLabel#statusLabel {
            color: #a1a1aa;
        }
        """
    )


def _apply_light(app: QtWidgets.QApplication):
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#f4f3f1"))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#1f2937"))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor("#ffffff"))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#eeece8"))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor("#1f2937"))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor("#ffffff"))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#1f2937"))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#4a5568"))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))
    app.setPalette(palette)

    app.setStyleSheet(
        """
        QWidget {
            font-size: 13px;
            font-family: "Inter", "Segoe UI", "SF Pro Text", "Arial";
            color: #1f2937;
        }
        QMainWindow {
            background-color: #f4f3f1;
        }
        QDialog#loginDialog {
            background: #f4f3f1;
        }
        QFrame#loginFrame {
            background: #ffffff;
            border: 1px solid #d8d3cb;
            border-radius: 12px;
        }
        QFrame#windowFrame {
            background: #f4f3f1;
            border: 1px solid #d8d3cb;
            border-radius: 12px;
        }
        QDialog#confirmDialog {
            background: #f4f3f1;
            border: 1px solid #d8d3cb;
            border-radius: 12px;
        }
        QFrame#confirmFrame {
            background: #ffffff;
            border: 1px solid #d8d3cb;
            border-radius: 12px;
        }
        QWidget#titleBar {
            background: #f8f6f3;
            border-bottom: 1px solid #d8d3cb;
        }
        QLabel#loginTitle {
            font-size: 20px;
            font-weight: 600;
        }
        QLabel#loginSubtitle {
            color: #64748b;
        }
        QTabWidget::pane {
            border: none;
        }
        QTabBar::tab {
            background: transparent;
            color: #6b7280;
            padding: 6px 12px;
        }
        QTabBar::tab:selected {
            color: #1f2937;
            border-bottom: 2px solid #4a5568;
        }
        QFrame#sidebar {
            background: #f9f7f4;
            border: 1px solid #d8d3cb;
            border-radius: 16px;
        }
        QPushButton#navButton {
            text-align: left;
            padding: 10px 12px;
            border-radius: 10px;
            background: transparent;
            border: 1px solid transparent;
            color: #1f2937;
        }
        QPushButton#navButton[collapsed="true"] {
            text-align: center;
            padding: 10px 0;
            color: #1f2937;
        }
        QPushButton#navButton:checked {
            background: #ece8e1;
            border: 1px solid #ddd7ce;
            color: #111827;
        }
        QToolButton#sidebarToggle {
            background: #ece8e1;
            border: 1px solid #ddd7ce;
            border-radius: 10px;
            padding: 6px 8px;
            color: #1f2937;
        }
        QToolButton#sidebarToggle:hover {
            background: #e3ddd4;
        }
        QFrame#profileCard {
            background: #f1ece5;
            border: 1px solid #ddd7ce;
            border-radius: 14px;
        }
        QPushButton#avatarButton {
            background: #e2dbd2;
            border: 1px solid #d0c6ba;
            border-radius: 16px;
            min-width: 32px;
            min-height: 32px;
            max-width: 32px;
            max-height: 32px;
            padding: 0;
            color: #1f2937;
        }
        QPushButton#avatarButton:hover {
            background: #d8cec2;
        }
        QLabel#profileName {
            font-weight: 600;
            color: #1f2937;
        }
        QLabel#profileRole {
            color: #6b7280;
        }
        QPushButton#ghostButton {
            background: transparent;
            border: 1px solid #d8d3cb;
            color: #1f2937;
        }
        QPushButton#ghostButton:hover {
            background: #ece8e1;
        }
        QPushButton#dangerButton {
            background: #fee2e2;
            border: 1px solid #fecaca;
            color: #991b1b;
        }
        QPushButton#dangerButton:hover {
            background: #fecaca;
        }
        QPushButton#panicButton {
            background: #991b1b;
            border: 1px solid #7f1d1d;
            color: #ffffff;
            font-size: 16px;
            font-weight: 700;
            padding: 14px 20px;
            border-radius: 90px;
        }
        QPushButton#panicButton:hover {
            background: #7f1d1d;
        }
        QPushButton#primaryButton {
            background: #3f4a5a;
            border: 1px solid #3f4a5a;
            color: #ffffff;
        }
        QPushButton#primaryButton:hover {
            background: #374151;
        }
        QPushButton#primaryOutlineButton {
            background: transparent;
            border: 2px solid #3f4a5a;
            color: #3f4a5a;
            font-size: 14px;
            font-weight: 600;
        }
        QPushButton#primaryOutlineButton:hover {
            background: #ece8e1;
        }
        QListWidget {
            background: #ffffff;
            border: 1px solid #d8d3cb;
            border-radius: 12px;
            padding: 8px;
        }
        QListWidget::item {
            padding: 10px 12px;
            border-radius: 8px;
            color: #1f2937;
        }
        QListWidget::item:selected {
            background: #3f4a5a;
            color: #ffffff;
        }
        QPushButton {
            padding: 8px 14px;
            border-radius: 10px;
            background: #3f4a5a;
            color: #ffffff;
            border: 1px solid #3f4a5a;
        }
        QPushButton:hover {
            background: #374151;
        }
        QPushButton:pressed {
            background: #2f3744;
        }
        QPushButton[active="true"] {
            background: #3f4a5a;
            border: 1px solid #3f4a5a;
            color: #ffffff;
        }
        QPushButton#titleButton, QPushButton#titleButtonClose {
            min-width: 28px;
            max-width: 28px;
            min-height: 24px;
            max-height: 24px;
            padding: 0;
            border-radius: 6px;
            background: #f1f5fb;
            color: #1f2937;
            border: 1px solid #d8d3cb;
        }
        QPushButton#titleButtonClose {
            background: #fee2e2;
            border: 1px solid #fecaca;
            color: #991b1b;
        }
        QPushButton#titleButtonClose:hover {
            background: #fecaca;
        }
        QPushButton[compact="true"] {
            padding: 4px 8px;
            font-size: 12px;
        }
        QLineEdit, QComboBox, QTableWidget, QTabWidget::pane, QSlider, QGroupBox {
            background: #ffffff;
            border: 1px solid #d8d3cb;
            border-radius: 10px;
            padding: 8px;
            color: #1f2937;
        }
        QGroupBox::title {
            color: #6b7280;
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
        }
        QHeaderView::section {
            background: #f3efe9;
            border: 1px solid #d8d3cb;
            padding: 8px;
            color: #1f2937;
        }
        QLabel#appTitle {
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
        }
        QLabel#sectionTitle {
            font-size: 14px;
            font-weight: 600;
            color: #1f2937;
        }
        QLabel#badge {
            background: #ece8e1;
            border: 1px solid #ddd7ce;
            border-radius: 10px;
            padding: 6px 10px;
            color: #1f2937;
        }
        QLabel#statusLabel {
            color: #6b7280;
        }
        """
    )


def _apply_neon(app: QtWidgets.QApplication):
    _apply_dark(app)
    app.setStyleSheet(
        app.styleSheet()
        + """
        QMainWindow {
            background-color: #111827;
        }
        QFrame#windowFrame, QFrame#loginFrame, QDialog#confirmDialog {
            background: #111827;
            border: 1px solid #273349;
        }
        QWidget#titleBar {
            background: #111827;
            border-bottom: 1px solid #273349;
        }
        QFrame#sidebar {
            background: #131d2d;
            border: 1px solid #273349;
        }
        QPushButton#primaryButton {
            background: #14b8a6;
            border: 1px solid #14b8a6;
            color: #0b1220;
        }
        QPushButton#primaryButton:hover {
            background: #0f9f90;
        }
        QPushButton#primaryOutlineButton {
            border: 2px solid #14b8a6;
            color: #2dd4bf;
        }
        QPushButton#primaryOutlineButton:hover {
            background: #1a2a3a;
        }
        QPushButton#panicButton {
            background: #f43f5e;
            border: 1px solid #f43f5e;
            color: #ffffff;
        }
        QPushButton#panicButton:hover {
            background: #e11d48;
        }
        QTabBar::tab:selected {
            color: #e6f7ff;
            border-bottom: 2px solid #14b8a6;
        }
        QPushButton[active="true"], QPushButton#navButton:checked {
            background: #1a2a3a;
            border: 1px solid #2b425b;
            color: #7ee7da;
        }
        QLabel#statusLabel {
            color: #9ab0c7;
        }
        """
    )


def _apply_pastel(app: QtWidgets.QApplication):
    _apply_light(app)
    app.setStyleSheet(
        app.styleSheet()
        + """
        QMainWindow {
            background-color: #f8f5f2;
        }
        QFrame#windowFrame, QDialog#confirmDialog {
            background: #f8f5f2;
            border: 1px solid #ddd5cc;
        }
        QFrame#loginFrame {
            border: 1px solid #ddd5cc;
        }
        QWidget#titleBar {
            background: #fdf8f4;
            border-bottom: 1px solid #ddd5cc;
        }
        QFrame#sidebar {
            background: #fbf8f5;
            border: 1px solid #ddd5cc;
        }
        QPushButton#primaryButton {
            background: #8b7fa8;
            border: 1px solid #8b7fa8;
            color: #ffffff;
        }
        QPushButton#primaryButton:hover {
            background: #7a6f96;
        }
        QPushButton#primaryOutlineButton {
            border: 2px solid #8b7fa8;
            color: #8b7fa8;
        }
        QPushButton#primaryOutlineButton:hover {
            background: #f0ebe4;
        }
        QPushButton#panicButton {
            background: #d9869a;
            border: 1px solid #d9869a;
            color: #ffffff;
        }
        QPushButton#panicButton:hover {
            background: #c87589;
        }
        QTabBar::tab:selected {
            color: #4b5563;
            border-bottom: 2px solid #8b7fa8;
        }
        QPushButton#navButton:checked {
            background: #eee9e2;
            border: 1px solid #ddd5cc;
            color: #1f2937;
        }
        QPushButton#navButton, QPushButton#navButton[collapsed="true"] {
            color: #1f2937;
        }
        QLabel#statusLabel {
            color: #6b7280;
        }
        """
    )
