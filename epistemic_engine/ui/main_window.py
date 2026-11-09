"""Premium main window � Anthropic style."""
import os, json
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QListWidget, QTextEdit, QLabel, QFileDialog, QMessageBox,
    QComboBox, QLineEdit, QFormLayout, QFrame)
from PySide6.QtCore import Qt
from .graph_view import GraphView
from .graph3d import Graph3DView
from .heatmap_view import HeatmapView
from .theme import THEME_QSS, COLORS
from ..core.knowledge_item import KnowledgeItem, EpistemicCategory, ValidationStatus
from ..core.graph import KnowledgeGraph, Edge
from ..core.analysis import detect_contradictions, missing_information, prioritize_experiments
from ..core.storage import Storage
from ..benchmark.runner import run_benchmark


class StatCard(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setStyleSheet("QFrame { background: #23211e; border: 1px solid #3d3a34; border-radius: 12px; }")
        lay = QVBoxLayout(self)
        t = QLabel(title); t.setStyleSheet("color: #a89f91; font-size: 11px; text-transform: uppercase;")
        v = QLabel(value); v.setStyleSheet("font-size: 22px; font-weight: 800; color: #d97757;")
        lay.addWidget(t); lay.addWidget(v)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Epistemic Engine")
        self.resize(1366, 768)
        self.setStyleSheet(THEME_QSS)
        self.graph = KnowledgeGraph()
        self.hypotheses: list = []
        self.db_path = os.path.join(os.getcwd(), "epistemic.db")
        self.storage = Storage(self.db_path)
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        # header
        header = QFrame()
        header.setStyleSheet("background: #23211e; border-bottom: 1px solid #3d3a34;")
        hl = QHBoxLayout(header)
        logo = QLabel("DM")
        logo.setStyleSheet("background: #d97757; color: #191817; font-weight: 800; padding: 6px; border-radius: 8px;")
        title = QLabel("Epistemic Engine")
        title.setStyleSheet("font-size: 20px; font-weight: 800;")
        sub = QLabel("Known � Unknown � Uncertain � Contradictory � Unsupported")
        sub.setStyleSheet("color: #a89f91;")
        hl.addWidget(logo); hl.addWidget(title); hl.addWidget(sub)
        hl.addStretch()
        self.btn_new = QPushButton("+ New Item"); self.btn_new.setObjectName("primary")
        self.btn_save = QPushButton("Save"); self.btn_load = QPushButton("Load")
        self.btn_sample = QPushButton("Load Sample"); self.btn_report = QPushButton("Report")
        for b in (self.btn_new, self.btn_save, self.btn_load, self.btn_sample, self.btn_report):
            hl.addWidget(b)
        root.addWidget(header)
        # stats row
        stats = QHBoxLayout()
        self.stat_total = StatCard("Items", "0"); self.stat_known = StatCard("Known", "0")
        self.stat_contra = StatCard("Contradictions", "0"); self.stat_gap = StatCard("Gaps", "0")
        for s in (self.stat_total, self.stat_known, self.stat_contra, self.stat_gap):
            stats.addWidget(s)
        root.addLayout(stats)
        # tabs
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)
        gtab = QWidget(); gl = QHBoxLayout(gtab)
        self.graph_view = Graph3DView(); gl.addWidget(self.graph_view, 3)
        self.item_list = QListWidget(); gl.addWidget(self.item_list, 1)
        self.tabs.addTab(gtab, "? Knowledge Graph")
        etab = QWidget(); el = QVBoxLayout(etab)
        self.evidence_text = QTextEdit(); el.addWidget(self.evidence_text)
        self.tabs.addTab(etab, "? Evidence")
        htab = QWidget(); hl2 = QVBoxLayout(htab)
        self.hyp_list = QListWidget(); hl2.addWidget(self.hyp_list)
        self.hyp_text = QTextEdit(); hl2.addWidget(self.hyp_text)
        self.tabs.addTab(htab, "? Hypotheses")
        self.heatmap = HeatmapView(); self.tabs.addTab(self.heatmap, "? Uncertainty Heatmap")
        atab = QWidget(); al = QVBoxLayout(atab)
        self.analysis_text = QTextEdit(); al.addWidget(self.analysis_text)
        btn_a = QPushButton("? Run Analysis"); btn_a.setObjectName("primary"); btn_a.clicked.connect(self.run_analysis); al.addWidget(btn_a)
        self.tabs.addTab(atab, "? Analysis")
        btab = QWidget(); bl = QVBoxLayout(btab)
        self.bench_text = QTextEdit(); bl.addWidget(self.bench_text)
        btn_b = QPushButton("? Run Benchmark"); btn_b.setObjectName("primary"); btn_b.clicked.connect(self.run_benchmark); bl.addWidget(btn_b)
        self.tabs.addTab(btab, "? Benchmark")
        rtab = QWidget(); rl = QVBoxLayout(rtab)
        self.report_text = QTextEdit(); rl.addWidget(self.report_text)
        self.tabs.addTab(rtab, "? Report")
        self.statusBar().showMessage("Ready")
        # wire
        self.btn_new.clicked.connect(self.new_item_dialog)
        self.btn_save.clicked.connect(self.save_graph)
        self.btn_load.clicked.connect(self.load_graph)
        self.btn_sample.clicked.connect(self.load_sample)
        self.btn_report.clicked.connect(self.generate_report)
        self.item_list.itemClicked.connect(self.show_item)
        self.refresh_all()

    def refresh_all(self):
        self.graph_view.render_graph(self.graph)
        self.item_list.clear()
        for it in self.graph.nodes.values():
            self.item_list.addItem(f"{it.statement[:44]}  [{it.category.value}]")
        self.heatmap.render(list(self.graph.nodes.values()))
        self.hyp_list.clear()
        for h in self.hypotheses:
            self.hyp_list.addItem(f"{h.title}  �  posterior {h.posterior:.2f}")
        items = list(self.graph.nodes.values())
        known = sum(1 for i in items if i.category.value == "known")
        contra = len(detect_contradictions(items))
        gaps = len(missing_information(items))
        # update stat cards (rebuild labels)
        for card, val in [(self.stat_total, len(items)), (self.stat_known, known), (self.stat_contra, contra), (self.stat_gap, gaps)]:
            card.findChild(QLabel).__class__  # noop
            labs = card.findChildren(QLabel)
            if len(labs) >= 2:
                labs[1].setText(str(val))
        self.statusBar().showMessage(f"{len(items)} items � {contra} contradictions � {gaps} gaps")

    def new_item_dialog(self):
        from PySide6.QtWidgets import QDialog, QDialogButtonBox
        dlg = QDialog(self); dlg.setWindowTitle("New Knowledge Item"); dlg.setStyleSheet(THEME_QSS)
        form = QFormLayout(dlg)
        stmt = QLineEdit(); cat = QComboBox(); cat.addItems([c.value for c in EpistemicCategory])
        vs = QComboBox(); vs.addItems([v.value for v in ValidationStatus])
        su = QLineEdit("0.8"); lc = QLineEdit("0.5")
        form.addRow("Statement", stmt); form.addRow("Category", cat); form.addRow("Validation", vs)
        form.addRow("Statistical Uncertainty", su); form.addRow("LM Confidence", lc)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); form.addRow(btns)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject)
        if dlg.exec():
            it = KnowledgeItem(statement=stmt.text(), category=EpistemicCategory(cat.currentText()),
                validation_status=ValidationStatus(vs.currentText()),
                statistical_uncertainty=float(su.text()), lm_confidence=float(lc.text()))
            self.graph.add_item(it); self.refresh_all()

    def show_item(self, item):
        idx = self.item_list.row(item); ids = list(self.graph.nodes.keys())
        if idx < len(ids):
            it = self.graph.nodes[ids[idx]]
            self.evidence_text.setText(json.dumps(it.to_dict(), indent=2))

    def save_graph(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "JSON (*.json)")
        if path:
            with open(path, "w") as f: json.dump(self.graph.to_dict(), f, indent=2)
            self.storage.save("default", self.graph); QMessageBox.information(self, "Saved", "Graph saved.")

    def load_graph(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Graph", "", "JSON (*.json)")
        if path:
            with open(path) as f: d = json.load(f)
            self.graph = KnowledgeGraph.from_dict(d); self.refresh_all()

    def load_sample(self):
        from ..core.sample_data import build_sample
        self.graph, self.hypotheses = build_sample(); self.refresh_all()

    def run_analysis(self):
        items = list(self.graph.nodes.values())
        contras = detect_contradictions(items); gaps = missing_information(items); ranked = prioritize_experiments(gaps, items)
        txt = "=== Contradictions ===\n"
        for c in contras: txt += f"{c[0]} <-> {c[1]}: {c[2]}\n"
        txt += "\n=== Missing Information ===\n"
        for g in gaps: txt += f"{g['item_id']}: {g['gap']} (severity {g['severity']})\n"
        txt += "\n=== Experiment Prioritization ===\n"
        for r in ranked: txt += f"Priority {r['priority']}: {r['item_id']} gain={r['expected_info_gain']}\n"
        self.analysis_text.setText(txt)

    def run_benchmark(self):
        res = run_benchmark(); self.bench_text.setText(json.dumps(res, indent=2))

    def generate_report(self):
        items = list(self.graph.nodes.values())
        known = sum(1 for i in items if i.category.value == "known"); unknown = sum(1 for i in items if i.category.value == "unknown")    # noqa
        txt = "# Epistemic Engine Research Report\n\n"
        txt += f"Total: {len(items)}\nKnown: {known}, Unknown: {unknown}\nHypotheses: {len(self.hypotheses)}\n"
        txt += f"Contradictions: {len(detect_contradictions(items))}\nGaps: {len(missing_information(items))}\n\n## Items\n"
        for it in items: txt += f"- [{it.category.value}] {it.statement} (stat_unc={it.statistical_uncertainty:.2f}, lm_conf={it.lm_confidence:.2f})\n"
        self.report_text.setText(txt)
        with open("research_report.md", "w") as f: f.write(txt)
