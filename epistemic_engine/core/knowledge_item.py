import uuid
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class ValidationStatus(Enum):
    UNKNOWN = "unknown"
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    CONTRADICTED = "contradicted"
    PARTIAL = "partial"


class EpistemicCategory(Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    UNCERTAIN = "uncertain"
    CONTRADICTORY = "contradictory"
    UNSUPPORTED = "unsupported"


class SourceType(Enum):
    LITERATURE = "literature"
    EXPERIMENT = "experiment"
    MODEL = "model"
    EXPERT = "expert"
    DATASET = "dataset"
    OBSERVATION = "observation"


@dataclass
class Source:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    source_type: SourceType = SourceType.LITERATURE
    reliability: float = 0.5  # 0..1 statistical reliability
    url: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name,
            "source_type": self.source_type.value,
            "reliability": self.reliability, "url": self.url,
            "metadata": self.metadata,
        }


@dataclass
class Revision:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    author: str = "system"
    change: str = ""
    previous_status: Optional[str] = None
    new_status: Optional[str] = None


@dataclass
class KnowledgeItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    statement: str = ""
    category: EpistemicCategory = EpistemicCategory.UNKNOWN
    validation_status: ValidationStatus = ValidationStatus.UNKNOWN
    sources: List[Source] = field(default_factory=list)
    # statistical uncertainty: variance/CI based, 0..1 (1 = high uncertainty)
    statistical_uncertainty: float = 1.0
    # subjective LM confidence: model self-reported, 0..1 (1 = high confidence)
    lm_confidence: float = 0.5
    revisions: List[Revision] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def add_revision(self, change, author="system", prev=None, new=None):
        self.revisions.append(Revision(author=author, change=change,
                                      previous_status=prev, new_status=new))
        self.updated_at = time.time()

    def combined_uncertainty(self):
        # distinguish statistical from subjective: weighted blend, statistical dominates
        return 0.6 * self.statistical_uncertainty + 0.4 * (1.0 - self.lm_confidence)

    def to_dict(self):
        return {
            "id": self.id, "statement": self.statement,
            "category": self.category.value,
            "validation_status": self.validation_status.value,
            "sources": [s.to_dict() for s in self.sources],
            "statistical_uncertainty": self.statistical_uncertainty,
            "lm_confidence": self.lm_confidence,
            "revisions": [{"id": r.id, "timestamp": r.timestamp, "author": r.author,
                           "change": r.change, "previous_status": r.previous_status,
                           "new_status": r.new_status} for r in self.revisions],
            "tags": self.tags, "metadata": self.metadata,
            "created_at": self.created_at, "updated_at": self.updated_at,
        }
