from PySide6 import QtGui, QtWidgets


def apply_theme(app: QtWidgets.QApplication, theme: str):
    theme = theme if theme in ("dark", "light") else "dark"
    app.setProperty("theme", theme)
    app.setStyle("Fusion")
    if theme == "light":
        _apply_light(app)
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
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#ffffff"))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#0f172a"))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor("#f8fafc"))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#f1f5f9"))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor("#0f172a"))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor("#ffffff"))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#0f172a"))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#0f172a"))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#ffffff"))
    app.setPalette(palette)

    app.setStyleSheet(
        """
        QWidget {
            font-size: 13px;
            font-family: "Inter", "Segoe UI", "SF Pro Text", "Arial";
            color: #0f172a;
        }
        QMainWindow {
            background-color: #ffffff;
        }
        QDialog#loginDialog {
            background: #ffffff;
        }
        QFrame#loginFrame {
            background: #ffffff;
            border: 1px solid #000000;
            border-radius: 12px;
        }
        QFrame#windowFrame {
            background: #ffffff;
            border: 1px solid #000000;
            border-radius: 12px;
        }
        QDialog#confirmDialog {
            background: #ffffff;
            border: 1px solid #000000;
            border-radius: 12px;
        }
        QFrame#confirmFrame {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
        }
        QWidget#titleBar {
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
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
            color: #64748b;
            padding: 6px 12px;
        }
        QTabBar::tab:selected {
            color: #0f172a;
            border-bottom: 2px solid #0f172a;
        }
        QFrame#sidebar {
            background: #ffffff;
            border: 1px solid #e2e8f0;
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
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
        }
        QToolButton#sidebarToggle {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 6px 8px;
        }
        QToolButton#sidebarToggle:hover {
            background: #e2e8f0;
        }
        QFrame#profileCard {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
        }
        QPushButton#avatarButton {
            background: #e2e8f0;
            border: 1px solid #cbd5f5;
            border-radius: 16px;
            min-width: 32px;
            min-height: 32px;
            max-width: 32px;
            max-height: 32px;
            padding: 0;
            color: #0f172a;
        }
        QPushButton#avatarButton:hover {
            background: #cbd5f5;
        }
        QLabel#profileName {
            font-weight: 600;
        }
        QLabel#profileRole {
            color: #64748b;
        }
        QPushButton#ghostButton {
            background: transparent;
            border: 1px solid #e2e8f0;
            color: #0f172a;
        }
        QPushButton#ghostButton:hover {
            background: #f1f5f9;
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
            background: #0f172a;
            border: 1px solid #0f172a;
            color: #ffffff;
        }
        QPushButton#primaryButton:hover {
            background: #111827;
        }
        QPushButton#primaryOutlineButton {
            background: transparent;
            border: 2px solid #0f172a;
            color: #0f172a;
            font-size: 14px;
            font-weight: 600;
        }
        QPushButton#primaryOutlineButton:hover {
            background: #f1f5f9;
        }
        QListWidget {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 8px;
        }
        QListWidget::item {
            padding: 10px 12px;
            border-radius: 8px;
            color: #0f172a;
        }
        QListWidget::item:selected {
            background: #0f172a;
            color: #ffffff;
        }
        QPushButton {
            padding: 8px 14px;
            border-radius: 10px;
            background: #0f172a;
            color: #ffffff;
            border: 1px solid #0f172a;
        }
        QPushButton:hover {
            background: #111827;
        }
        QPushButton:pressed {
            background: #0b1220;
        }
        QPushButton[active="true"] {
            background: #0f172a;
            border: 1px solid #0f172a;
            color: #ffffff;
        }
        QPushButton#titleButton, QPushButton#titleButtonClose {
            min-width: 28px;
            max-width: 28px;
            min-height: 24px;
            max-height: 24px;
            padding: 0;
            border-radius: 6px;
            background: #f1f5f9;
            color: #0f172a;
            border: 1px solid #e2e8f0;
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
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 8px;
            color: #0f172a;
        }
        QGroupBox::title {
            color: #64748b;
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
        }
        QHeaderView::section {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 8px;
            color: #0f172a;
        }
        QLabel#appTitle {
            font-size: 18px;
            font-weight: 600;
            color: #0f172a;
        }
        QLabel#sectionTitle {
            font-size: 14px;
            font-weight: 600;
            color: #0f172a;
        }
        QLabel#badge {
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 6px 10px;
            color: #0f172a;
        }
        QLabel#statusLabel {
            color: #64748b;
        }
        """
    )
