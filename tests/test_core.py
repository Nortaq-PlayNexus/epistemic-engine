"""Tests for core."""
import sys, os
sys.path.insert(0, os.path.abspath("."))
from epistemic_engine.core.knowledge_item import KnowledgeItem, EpistemicCategory, ValidationStatus
from epistemic_engine.core.graph import KnowledgeGraph, Edge
from epistemic_engine.core.analysis import detect_contradictions, missing_information, prioritize_experiments
from epistemic_engine.benchmark.runner import run_benchmark


def test_item_combined_uncertainty():
    it = KnowledgeItem(statistical_uncertainty=0.8, lm_confidence=0.9)
    assert 0 <= it.combined_uncertainty() <= 1


def test_graph_add_remove():
    g = KnowledgeGraph()
    it = KnowledgeItem(statement="x")
    g.add_item(it)
    assert it.id in g.nodes
    g.remove_item(it.id)
    assert it.id not in g.nodes


def test_contradiction_edge():
    g = KnowledgeGraph()
    a = KnowledgeItem(statement="Drug X works")
    b = KnowledgeItem(statement="Drug X does not work")
    g.add_item(a); g.add_item(b)
    g.add_edge(Edge(source=a.id, target=b.id, relation="contradicts"))
    assert (a.id, b.id) in g.find_contradictions() or (b.id, a.id) in g.find_contradictions()


def test_missing_info():
    it = KnowledgeItem(statement="x", statistical_uncertainty=0.9)
    gaps = missing_information([it])
    assert len(gaps) > 0


def test_prioritize():
    gaps = [{"item_id": "a", "gap": "g", "severity": 0.9}]
    ranked = prioritize_experiments(gaps, [])
    assert ranked[0]["priority"] == 1


def test_benchmark():
    r = run_benchmark(seeds=10)
    assert "baseline_accuracy" in r
    assert "uncertainty_aware_accuracy" in r


def test_revision_history():
    it = KnowledgeItem(statement="x")
    it.add_revision("created", prev=None, new="unknown")
    assert len(it.revisions) == 1


def test_storage_roundtrip(tmp_path):
    from epistemic_engine.core.storage import Storage
    from epistemic_engine.core.sample_data import build_sample
    g, _ = build_sample()
    db = str(tmp_path / "t.db")
    st = Storage(db)
    st.save("g", g)
    g2 = st.load("g")
    assert len(g2.nodes) == len(g.nodes)
