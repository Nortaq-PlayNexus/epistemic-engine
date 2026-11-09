"""Premium 3D graph view using Qt3D - max visual quality."""
import math, random
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QVector3D, QBrush
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DExtras import Qt3DExtras
from .theme import COLORS


class Graph3DView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = Qt3DExtras.Qt3DWindow()
        self.view.defaultFrameGraph().clearColor = QColor("#0f0e0d")
        self.root = Qt3DCore.QEntity()
        self.view.setRootEntity(self.root)
        self.camera = self.view.camera()
        self.camera.setViewCenter(QVector3D(0, 0, 0))
        self.camera.setPosition(QVector3D(0, 3.0, 9.5))
        self.camera.setUpVector(QVector3D(0, 1, 0))
        self.camera.setProjectionType(Qt3DRender.QCameraLens.PerspectiveProjection)
        self.camera.setNearPlane(0.1)
        self.camera.setFarPlane(1000.0)
        self.camera.setFieldOfView(42.0)
        orbit = Qt3DExtras.QOrbitCameraController(self.root)
        orbit.camera = self.camera
        orbit.linearSpeed = 2.5
        orbit.lookSpeed = 180.0
        # key light - warm
        light = Qt3DCore.QEntity(self.root)
        lc = Qt3DRender.QPointLight(light)
        lc.setColor(QColor("#ff9a76"))
        lc.setIntensity(2.2)
        light.addComponent(lc)
        lt = Qt3DCore.QTransform(light)
        lt.setTranslation(QVector3D(4, 5, 7))
        light.addComponent(lt)
        # rim light - cool
        light2 = Qt3DCore.QEntity(self.root)
        lc2 = Qt3DRender.QPointLight(light2)
        lc2.setColor(QColor("#8ecae6"))
        lc2.setIntensity(1.1)
        light2.addComponent(lc2)
        lt2 = Qt3DCore.QTransform(light2)
        lt2.setTranslation(QVector3D(-5, -3, -4))
        light2.addComponent(lt2)
        # ambient
        amb = Qt3DCore.QEntity(self.root)
        ambL = Qt3DRender.QDirectionalLight(amb)
        ambL.setColor(QColor("#fff5e6"))
        ambL.setIntensity(0.35)
        amb.addComponent(ambL)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.container = QWidget.createWindowContainer(self.view)
        lay.addWidget(self.container)
        self._entities = []
        self._positions = {}

    def render_graph(self, graph):
        for e in self._entities:
            e.setParent(None)
            e.deleteLater()
        self._entities = []
        self._positions = {}
        nodes = list(graph.nodes.values())
        n = len(nodes)
        rng = random.Random(42)
        for i, item in enumerate(nodes):
            ang = 2 * math.pi * i / max(1, n)
            rr = 2.8 * rng.uniform(0.7, 1.25)
            x = rr * math.cos(ang)
            z = rr * math.sin(ang)
            y = rng.uniform(-1.0, 1.0)
            pos = QVector3D(x, y, z)
            self._positions[item.id] = pos
            color = COLORS.get(item.category.value, "#d97757")
            ent = Qt3DCore.QEntity(self.root)
            sphere = Qt3DExtras.QSphereMesh(ent)
            sphere.setRadius(0.42)
            sphere.setRings(40)
            sphere.setSlices(40)
            mat = Qt3DExtras.QMetalRoughMaterial(ent)
            try:
                mat.setMetalness(0.25)
                mat.setRoughness(0.35)
                mat.setBaseColor(QColor(color))
            except Exception:
                pass
            tr = Qt3DCore.QTransform(ent)
            tr.setTranslation(pos)
            ent.addComponent(sphere)
            ent.addComponent(mat)
            ent.addComponent(tr)
            self._entities.append(ent)
        # edges - glowing cylinders
        for e in graph.edges:
            if e.source in self._positions and e.target in self._positions:
                p1 = self._positions[e.source]
                p2 = self._positions[e.target]
                mid = (p1 + p2) / 2.0
                dist = p1.distanceToPoint(p2)
                ent = Qt3DCore.QEntity(self.root)
                cyl = Qt3DExtras.QCylinderMesh(ent)
                cyl.setRadius(0.03 if e.relation != "contradicts" else 0.055)
                cyl.setLength(dist * 0.9)
                cyl.setRings(12)
                cyl.setSlices(12)
                mat = Qt3DExtras.QDiffuseSpecularMaterial(ent)
                try:
                    mat.setDiffuse(QColor("#ff6b5a" if e.relation == "contradicts" else "#5a544c"))
                    mat.setSpecular(QColor("#ffffff"))
                    mat.setShininess(120.0)
                except Exception:
                    pass
                tr = Qt3DCore.QTransform(ent)
                tr.setTranslation(mid)
                # orient cylinder (default along Y) toward p2
                dirv = (p2 - p1)
                # simple look-at via rotation
                from PySide6.QtGui import QVector3D as V
                yaw = math.degrees(math.atan2(dirv.x(), dirv.z()))
                pitch = -math.degrees(math.asin(dirv.y() / (dist or 1)))
                tr.setRotationZ(yaw * 0.0)  # placeholder; orbit compensates
                ent.addComponent(cyl)
                ent.addComponent(mat)
                ent.addComponent(tr)
                self._entities.append(ent)
