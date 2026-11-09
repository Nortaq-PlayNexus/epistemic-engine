"""SQLite persistence for knowledge graph."""
import sqlite3, json, os
from typing import Optional
from .graph import KnowledgeGraph


class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._init()

    def _init(self):
        con = sqlite3.connect(self.db_path)
        con.execute("""CREATE TABLE IF NOT EXISTS graphs(
            id INTEGER PRIMARY KEY, name TEXT, data TEXT, updated REAL)""")
        con.commit()
        con.close()

    def save(self, name: str, graph: KnowledgeGraph):
        data = json.dumps(graph.to_dict())
        con = sqlite3.connect(self.db_path)
        cur = con.execute("SELECT id FROM graphs WHERE name=?", (name,))
        row = cur.fetchone()
        if row:
            con.execute("UPDATE graphs SET data=?, updated=strftime('%s','now') WHERE name=?", (data, name))
        else:
            con.execute("INSERT INTO graphs(name,data,updated) VALUES(?,?,strftime('%s','now'))", (name, data))
        con.commit()
        con.close()

    def load(self, name: str) -> Optional[KnowledgeGraph]:
        con = sqlite3.connect(self.db_path)
        cur = con.execute("SELECT data FROM graphs WHERE name=?", (name,))
        row = cur.fetchone()
        con.close()
        if not row:
            return None
        from .graph import KnowledgeGraph
        return KnowledgeGraph.from_dict(json.loads(row[0]))

    def list_graphs(self):
        con = sqlite3.connect(self.db_path)
        rows = con.execute("SELECT name FROM graphs").fetchall()
        con.close()
        return [r[0] for r in rows]
