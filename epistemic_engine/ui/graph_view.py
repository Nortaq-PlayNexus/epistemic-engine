"""Graph view widget."""
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt


class GraphView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(self.renderHints())
        self._positions = {}

    def render_graph(self, graph):
        self.scene.clear()
        self._positions = {}
        nodes = list(graph.nodes.values())
        n = len(nodes)
        import math
        cx, cy = 300, 250
        r = 180
        for i, item in enumerate(nodes):
            ang = 2 * math.pi * i / max(1, n)
            x = cx + r * math.cos(ang)
            y = cy + r * math.sin(ang)
            self._positions[item.id] = (x, y)
            # color by category
            color = {
                "known": "#2ecc71", "unknown": "#95a5a6",
                "uncertain": "#f39c12", "contradictory": "#e74c3c",
                "unsupported": "#8e44ad",
            }.get(item.category.value, "#3498db")
            el = self.scene.addEllipse(x - 20, y - 20, 40, 40, QPen(Qt.black), QBrush(QColor(color)))
            el.setToolTip(item.statement)
            txt = self.scene.addText(item.statement[:24], QFont("Arial", 8))
            txt.setPos(x - 30, y + 22)
        # edges
        for e in graph.edges:
            if e.source in self._positions and e.target in self._positions:
                x1, y1 = self._positions[e.source]
                x2, y2 = self._positions[e.target]
                pen = QPen(QColor("#e74c3c" if e.relation == "contradicts" else "#2c3e50"))
                pen.setWidth(2 if e.relation == "contradicts" else 1)
                self.scene.addLine(x1, y1, x2, y2, pen)
