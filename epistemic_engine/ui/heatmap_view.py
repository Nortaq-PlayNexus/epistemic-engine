"""Uncertainty heatmap widget."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


class HeatmapView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Uncertainty Heatmap")
        self.layout.addWidget(self.label)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

    def render(self, items):
        self.table.setRowCount(len(items))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Item", "Statistical", "LM conf", "Combined"])
        for i, it in enumerate(items):
            self.table.setItem(i, 0, QTableWidgetItem(it.statement[:40]))
            s = QTableWidgetItem(f"{it.statistical_uncertainty:.2f}")
            s.setBackground(QColor(self._color(it.statistical_uncertainty)))
            self.table.setItem(i, 1, s)
            c = QTableWidgetItem(f"{it.lm_confidence:.2f}")
            self.table.setItem(i, 2, c)
            cb = QTableWidgetItem(f"{it.combined_uncertainty():.2f}")
            cb.setBackground(QColor(self._color(it.combined_uncertainty())))
            self.table.setItem(i, 3, cb)

    def _color(self, v):
        # red high, green low
        r = int(255 * v)
        g = int(255 * (1 - v))
        return f"#{r:02x}{g:02x}60"
