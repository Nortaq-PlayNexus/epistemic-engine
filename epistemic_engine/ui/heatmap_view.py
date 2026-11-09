"""Premium uncertainty heatmap with gradient cards."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class HeatCard(QFrame):
    def __init__(self, item):
        super().__init__()
        self.setStyleSheet("QFrame { border: 1px solid #3d3a34; border-radius: 10px; background: #23211e; }")
        lay = QVBoxLayout(self)
        t = QLabel(item.statement[:48])
        t.setWordWrap(True)
        t.setStyleSheet("font-weight: 600;")
        lay.addWidget(t)
        bar = QLabel()
        lay.addWidget(bar)
        su = item.statistical_uncertainty
        lc = item.lm_confidence
        cb = item.combined_uncertainty()
        r = int(231 * cb)
        g = int(111 * (1 - cb) + 60)
        bar.setText(f"Statistical {su:.2f}    LM {lc:.2f}    Combined {cb:.2f}")
        bar.setStyleSheet(f"color: #{r:02x}{g:02x}57; font-weight: bold;")


class HeatmapView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scroll_layout = QVBoxLayout(self)
        self.title = QLabel("Uncertainty Heatmap  Statistical vs Subjective")
        self.title.setStyleSheet("font-size: 16px; font-weight: 700; color: #d97757;")
        self.scroll_layout.addWidget(self.title)
        self.grid = QGridLayout()
        self.scroll_layout.addLayout(self.grid)
        self.scroll_layout.addStretch()

    def render(self, items):
        # clear
        while self.grid.count():
            it = self.grid.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        for i, item in enumerate(items):
            self.grid.addWidget(HeatCard(item), i // 2, i % 2)
