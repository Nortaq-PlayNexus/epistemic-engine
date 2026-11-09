"""Premium 3D graph view using Qt3D."""
import math, random
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QVector3D
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DExtras import Qt3DExtras
from .theme import COLORS


class Graph3DView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = Qt3DExtras.Qt3DWindow()
        self.view.defaultFrameGraph().clearColor = QColor("#191817")
        self.root = Qt3DCore.QEntity()
        self.view.setRootEntity(self.root)
        self.camera = self.view.camera()
        self.camera.setViewCenter(QVector3D(0, 0, 0))
        self.camera.setPosition(QVector3D(0, 2.5, 8))
        self.camera.setUpVector(QVector3D(0, 1, 0))
        self.camera.setProjectionType(Qt3DRender.QCameraLens.PerspectiveProjection)
        self.camera.setNearPlane(0.1)
        self.camera.setFarPlane(1000.0)
        self.camera.setFieldOfView(45.0)
        orbit = Qt3DExtras.QOrbitCameraController(self.root)
        orbit.camera = self.camera
        # warm key light
        light = Qt3DCore.QEntity(self.root)
        lc = Qt3DRender.QPointLight(light)
        lc.setColor(QColor("#ff9770"))
        lc.setIntensity(1.4)
        light.addComponent(lc)
        lt = Qt3DCore.QTransform(light)
        lt.setTranslation(QVector3D(3, 4, 6))
        light.addComponent(lt)
        # cool fill light
        light2 = Qt3DCore.QEntity(self.root)
        lc2 = Qt3DRender.QPointLight(light2)
        lc2.setColor(QColor("#7a9e7e"))
        lc2.setIntensity(0.7)
        light2.addComponent(lc2)
        lt2 = Qt3DCore.QTransform(light2)
        lt2.setTranslation(QVector3D(-4, -2, -3))
        light2.addComponent(lt2)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.container = QWidget.createWindowContainer(self.view)
        lay.addWidget(self.container)
        self._entities = []

    def render_graph(self, graph):
        for e in self._entities:
            e.setParent(None)
            e.deleteLater()
        self._entities = []
        nodes = list(graph.nodes.values())
        n = len(nodes)
        rng = random.Random(42)
        for i, item in enumerate(nodes):
            ang = 2 * math.pi * i / max(1, n)
            rr = 2.4 * rng.uniform(0.75, 1.15)
            x = rr * math.cos(ang)
            z = rr * math.sin(ang)
            y = rng.uniform(-0.8, 0.8)
            color = COLORS.get(item.category.value, "#d97757")
            ent = Qt3DCore.QEntity(self.root)
            sphere = Qt3DExtras.QSphereMesh(ent)
            sphere.setRadius(0.38)
            sphere.setRings(32)
            sphere.setSlices(32)
            mat = Qt3DExtras.QDiffuseSpecularMaterial(ent)
            # QDiffuseSpecularMaterial uses diffuse color property via parameter model
            try:
                mat.setDiffuse(QColor(color))
            except Exception:
                pass
            try:
                mat.setSpecular(QColor("#ffffff"))
            except Exception:
                pass
            try:
                mat.setShininess(80.0)
            except Exception:
                pass
            tr = Qt3DCore.QTransform(ent)
            tr.setTranslation(QVector3D(x, y, z))
            ent.addComponent(sphere)
            ent.addComponent(mat)
            ent.addComponent(tr)
            self._entities.append(ent)
