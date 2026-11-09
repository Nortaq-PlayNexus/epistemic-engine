import uuid
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any
from .knowledge_item import KnowledgeItem, Source


@dataclass
class Hypothesis:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    supporting_items: List[str] = field(default_factory=list)  # KnowledgeItem ids
    contradicting_items: List[str] = field(default_factory=list)
    prior: float = 0.5
    posterior: float = 0.5
    status: str = "active"  # active, rejected, accepted
    revisions: List[Dict[str, Any]] = field(default_factory=list)

    def update_posterior(self, evidence_weight: float):
        # simple bayesian-ish update
        self.posterior = max(0.0, min(1.0, self.posterior * (1 + evidence_weight) / 2.0 + evidence_weight / 4.0))

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "description": self.description,
            "supporting_items": self.supporting_items,
            "contradicting_items": self.contradicting_items,
            "prior": self.prior, "posterior": self.posterior, "status": self.status,
            "revisions": self.revisions,
        }
