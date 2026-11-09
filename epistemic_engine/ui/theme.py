"""Anthropic-style dark theme."""
THEME_QSS = """
QMainWindow { background: #191817; }
QWidget { background: #191817; color: #ece7df; font-family: "Segoe UI", Inter, sans-serif; font-size: 13px; }
QPushButton { background: #2e2b27; color: #ece7df; border: 1px solid #3d3a34; border-radius: 8px; padding: 7px 14px; font-weight: 600; }
QPushButton:hover { background: #3d3a34; border-color: #d97757; }
QPushButton:pressed { background: #d97757; color: #191817; }
QPushButton#primary { background: #d97757; color: #191817; border: none; }
QPushButton#primary:hover { background: #e89a7e; }
QPushButton#ghost { background: transparent; border: 1px solid #3d3a34; }
QLineEdit, QTextEdit, QListWidget, QTableWidget, QComboBox { background: #23211e; border: 1px solid #3d3a34; border-radius: 8px; padding: 6px; selection-background-color: #d97757; }
QLineEdit:focus, QTextEdit:focus { border: 1px solid #d97757; }
QListWidget::item { padding: 8px; border-radius: 6px; margin: 2px; }
QListWidget::item:selected { background: #3d3a34; }
QListWidget::item:hover { background: #2e2b27; }
QTabWidget::pane { border: 1px solid #3d3a34; border-radius: 10px; background: #1e1c1a; }
QTabBar::tab { background: #23211e; color: #a89f91; padding: 8px 16px; border-radius: 8px 8px 0 0; margin-right: 4px; }
QTabBar::tab:selected { background: #2e2b27; color: #ece7df; }
QHeaderView::section { background: #2e2b27; color: #ece7df; padding: 6px; border: none; }
QStatusBar { background: #23211e; color: #a89f91; }
QToolTip { background: #2e2b27; color: #ece7df; border: 1px solid #d97757; padding: 6px; }
"""

COLORS = {
    "known": "#7fb069",
    "unknown": "#a89f91",
    "uncertain": "#e9c46a",
    "contradictory": "#e76f51",
    "unsupported": "#b5179e",
}
