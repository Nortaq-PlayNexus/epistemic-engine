"""Premium graph view with glow nodes and curved edges."""
import math, random
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPathItem, QGraphicsItem
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath, QRadialGradient
from PySide6.QtCore import Qt, QRectF
from .theme import COLORS


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, item, x, y, color):
        super().__init__(x - 18, y - 18, 36, 36)
        self.item = item
        self.setPen(QPen(QColor(color), 2))
        self.setBrush(QBrush(QColor(color)))
        self.setToolTip(f"{item.statement}\nCategory: {item.category.value}\nStat unc: {item.statistical_uncertainty:.2f}")
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)

    def hoverEnterEvent(self, e):
        self.setPen(QPen(QColor("#d97757"), 3))
        super().hoverEnterEvent(e)

    def hoverLeaveEvent(self, e):
        from .theme import COLORS
        self.setPen(QPen(QColor(COLORS.get(self.item.category.value, "#d97757")), 2))
        super().hoverLeaveEvent(e)


class GraphView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHints(self.renderHints())
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._pos = {}

    def wheelEvent(self, e):
        f = 1.15 if e.angleDelta().y() > 0 else 0.87
        self.scale(f, f)

    def render_graph(self, graph):
        self.scene.clear()
        self._pos = {}
        nodes = list(graph.nodes.values())
        n = len(nodes)
        cx, cy = 350, 280
        r = min(220, 90 + n * 18)
        # seeded layout for stability
        rng = random.Random(42)
        for i, item in enumerate(nodes):
            ang = 2 * math.pi * i / max(1, n) + rng.uniform(-0.15, 0.15)
            rr = r * rng.uniform(0.85, 1.05)
            x = cx + rr * math.cos(ang)
            y = cy + rr * math.sin(ang)
            self._pos[item.id] = (x, y)
        # curved edges first (behind nodes)
        for e in graph.edges:
            if e.source in self._pos and e.target in self._pos:
                x1, y1 = self._pos[e.source]
                x2, y2 = self._pos[e.target]
                midx = (x1 + x2) / 2
                midy = (y1 + y2) / 2 - 30
                path = QPainterPath()
                path.moveTo(x1, y1)
                path.quadTo(midx, midy, x2, y2)
                col = "#e76f51" if e.relation == "contradicts" else "#4a463f"
                pen = QPen(QColor(col), 2 if e.relation == "contradicts" else 1)
                pen.setStyle(Qt.DashLine if e.relation == "contradicts" else Qt.SolidLine)
                self.scene.addPath(path, pen)
        for item in nodes:
            x, y = self._pos[item.id]
            color = COLORS.get(item.category.value, "#d97757")
            # glow
            glow = self.scene.addEllipse(x - 26, y - 26, 52, 52, QPen(Qt.NoPen), QBrush(QColor(color + "40")))
            node = NodeItem(item, x, y, color)
            self.scene.addItem(node)
            txt = self.scene.addText(item.statement[:26] + ("" if len(item.statement) > 26 else ""), QFont("Segoe UI", 9, QFont.Bold))
            txt.setDefaultTextColor(QColor("#ece7df"))
            # pill background
            rect = txt.boundingRect().adjusted(-8, -2, 8, 4)
            bg = self.scene.addRect(QRectF(x - 60, y + 22, 120, 22), QPen(Qt.NoPen), QBrush(QColor("#23211e")))
            txt.setPos(x - 60, y + 24)
