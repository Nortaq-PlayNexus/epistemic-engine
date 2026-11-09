# Architecture

Epistemic Engine is a PySide6 desktop app with a pure-Python core.

## Components
- core/knowledge_item.py: KnowledgeItem, Source, Revision, enums
- core/graph.py: KnowledgeGraph (nodes + typed edges)
- core/analysis.py: contradiction detection, missing info, experiment prioritization
- core/storage.py: SQLite persistence
- core/sample_data.py: demo dataset
- ui/: PySide6 widgets (graph view, heatmap, main window)
- benchmark/runner.py: baseline vs uncertainty-aware comparison

## Data flow
UI -> KnowledgeGraph (in-memory) -> Storage (SQLite) / JSON export.
Analysis operates on KnowledgeItem list.
