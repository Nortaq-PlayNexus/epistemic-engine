"""Knowledge graph (pure python, no networkx)."""
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from .knowledge_item import KnowledgeItem


@dataclass
class Edge:
    source: str
    target: str
    relation: str = "supports"  # supports, contradicts, depends_on, derived_from
    weight: float = 1.0


class KnowledgeGraph:
    def __init__(self):
        self.nodes: Dict[str, KnowledgeItem] = {}
        self.edges: List[Edge] = []
        self.adj: Dict[str, List[Edge]] = {}

    def add_item(self, item: KnowledgeItem):
        self.nodes[item.id] = item
        self.adj.setdefault(item.id, [])

    def add_edge(self, e: Edge):
        if e.source in self.nodes and e.target in self.nodes:
            self.edges.append(e)
            self.adj.setdefault(e.source, []).append(e)

    def remove_item(self, item_id):
        if item_id in self.nodes:
            del self.nodes[item_id]
            self.edges = [e for e in self.edges if e.source != item_id and e.target != item_id]
            self.adj.pop(item_id, None)
            for k in list(self.adj.keys()):
                self.adj[k] = [e for e in self.adj[k] if e.target != item_id]

    def neighbors(self, item_id) -> List[Tuple[str, Edge]]:
        out = []
        for e in self.edges:
            if e.source == item_id:
                out.append((e.target, e))
            elif e.target == item_id:
                out.append((e.source, e))
        return out

    def find_contradictions(self) -> List[Tuple[str, str]]:
        pairs = []
        items = list(self.nodes.values())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                # explicit edge contradiction
                for e in self.edges:
                    if ((e.source == a.id and e.target == b.id) or (e.source == b.id and e.target == a.id)) and e.relation == "contradicts":
                        pairs.append((a.id, b.id))
                # semantic: both mention similar keywords but opposite polarity
        # dedup
        seen = set()
        uniq = []
        for p in pairs:
            key = tuple(sorted(p))
            if key not in seen:
                seen.add(key)
                uniq.append(p)
        return uniq

    def subgraph_by_tag(self, tag):
        g = KnowledgeGraph()
        for iid, item in self.nodes.items():
            if tag in item.tags:
                g.add_item(item)
        for e in self.edges:
            if e.source in g.nodes and e.target in g.nodes:
                g.add_edge(e)
        return g

    def to_dict(self):
        return {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": [{"source": e.source, "target": e.target, "relation": e.relation, "weight": e.weight} for e in self.edges],
        }

    @classmethod
    def from_dict(cls, d):
        g = cls()
        for k, v in d.get("nodes", {}).items():
            from .knowledge_item import KnowledgeItem, Source, EpistemicCategory, ValidationStatus
            item = KnowledgeItem(
                id=v["id"], statement=v["statement"],
                category=EpistemicCategory(v["category"]),
                validation_status=ValidationStatus(v["validation_status"]),
                statistical_uncertainty=v["statistical_uncertainty"],
                lm_confidence=v["lm_confidence"],
                tags=v.get("tags", []),
                metadata=v.get("metadata", {}),
                created_at=v.get("created_at", 0) or 0,
                updated_at=v.get("updated_at", 0) or 0,
            )
            for s in v.get("sources", []):
                item.sources.append(Source(id=s["id"], name=s["name"],
                                          reliability=s.get("reliability", 0.5),
                                          url=s.get("url", "")))
            g.add_item(item)
        for e in d.get("edges", []):
            g.add_edge(Edge(source=e["source"], target=e["target"],
                            relation=e["relation"], weight=e.get("weight", 1.0)))
        return g
