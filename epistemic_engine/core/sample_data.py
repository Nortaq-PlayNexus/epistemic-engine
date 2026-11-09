"""Sample data for demo."""
from ..core.knowledge_item import KnowledgeItem, Source, EpistemicCategory, ValidationStatus, SourceType
from ..core.hypothesis import Hypothesis
from ..core.graph import KnowledgeGraph, Edge


def build_sample():
    g = KnowledgeGraph()
    sources = [
        Source(name="RCT 2024", source_type=SourceType.LITERATURE, reliability=0.9),
        Source(name="Lab experiment", source_type=SourceType.EXPERIMENT, reliability=0.85),
    ]
    items = [
        KnowledgeItem(statement="Drug X reduces inflammation in mice", category=EpistemicCategory.KNOWN,
                      validation_status=ValidationStatus.SUPPORTED, sources=[sources[0]],
                      statistical_uncertainty=0.2, lm_confidence=0.85, tags=["drugx"]),
        KnowledgeItem(statement="Drug X has no effect on humans", category=EpistemicCategory.CONTRADICTORY,
                      validation_status=ValidationStatus.CONTRADICTED, sources=[sources[1]],
                      statistical_uncertainty=0.6, lm_confidence=0.4, tags=["drugx"]),
        KnowledgeItem(statement="Mechanism of Drug X unknown", category=EpistemicCategory.UNKNOWN,
                      validation_status=ValidationStatus.UNKNOWN, sources=[],
                      statistical_uncertainty=0.9, lm_confidence=0.3, tags=["drugx"]),
        KnowledgeItem(statement="Dosage 10mg optimal", category=EpistemicCategory.UNCERTAIN,
                      validation_status=ValidationStatus.PARTIAL, sources=[sources[1]],
                      statistical_uncertainty=0.5, lm_confidence=0.6, tags=["dosage"]),
        KnowledgeItem(statement="Side effects minimal", category=EpistemicCategory.UNSUPPORTED,
                      validation_status=ValidationStatus.UNSUPPORTED, sources=[],
                      statistical_uncertainty=0.95, lm_confidence=0.2, tags=["safety"]),
    ]
    for it in items:
        g.add_item(it)
    # edges
    if len(items) >= 2:
        g.add_edge(Edge(source=items[0].id, target=items[1].id, relation="contradicts"))
    hyps = [
        Hypothesis(title="Drug X is effective", description="Broad efficacy", prior=0.6, posterior=0.6),
        Hypothesis(title="Drug X ineffective in humans", description="Species-specific", prior=0.4, posterior=0.4),
    ]
    return g, hyps
