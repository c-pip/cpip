"""
Hierarchical Memory Architecture for SwarmDroid
- Short-term conversation memory
- Long-term persistent knowledge
- Agent-specific private memory
- Shared cross-agent memory
- Provenance and user-controlled deletion
"""

import sqlite3
import time
import json
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .vector_index import VectorIndex


class MemoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str  # "SHORT_TERM", "LONG_TERM", "AGENT_PRIVATE", "SHARED"
    agent_id: Optional[str] = None  # None for user/system wide
    key: str
    content: str
    tags: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)
    provenance: str = "user"  # "user", "MasterAgent", "ResearchAgent", etc.


class MemoryStore:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._vector_index = VectorIndex()
        self._init_sqlite()
        
        # In-memory buffer for active conversation (Short-term)
        self._active_conversation: List[Dict[str, Any]] = []
    
    def _init_sqlite(self):
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    agent_id TEXT,
                    key TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    timestamp REAL,
                    provenance TEXT
                )
            """)
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_cat ON memories(category)")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_agent ON memories(agent_id)")
    
    # --- Short-term memory (Active Conversation) ---
    def append_conversation(self, role: str, content: str, agent_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        entry = {
            "role": role,
            "content": content,
            "agent_id": agent_id,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self._active_conversation.append(entry)
        # Also index for rapid retrieval
        self._vector_index.add(
            f"conv_{len(self._active_conversation)}",
            content,
            {"type": "conversation", "role": role, "agent_id": agent_id}
        )
    
    def get_conversation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._active_conversation[-limit:]
    
    def clear_active_conversation(self):
        self._active_conversation.clear()
    
    # --- Persistent Long-term, Agent-specific, & Shared Memory ---
    def store(self, category: str, key: str, content: str, agent_id: Optional[str] = None, tags: Optional[List[str]] = None, provenance: str = "system") -> MemoryItem:
        item = MemoryItem(
            category=category,
            agent_id=agent_id,
            key=key,
            content=content,
            tags=tags or [],
            provenance=provenance
        )
        
        with self._conn:
            self._conn.execute("""
                INSERT OR REPLACE INTO memories (id, category, agent_id, key, content, tags, timestamp, provenance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id,
                item.category,
                item.agent_id,
                item.key,
                item.content,
                json.dumps(item.tags),
                item.timestamp,
                item.provenance
            ))
        
        # Add to semantic vector index
        self._vector_index.add(
            item.id,
            f"{item.key}: {item.content}",
            {"category": category, "agent_id": agent_id, "key": key, "provenance": provenance}
        )
        return item
    
    def retrieve(self, category: Optional[str] = None, agent_id: Optional[str] = None, key: Optional[str] = None) -> List[MemoryItem]:
        query = "SELECT id, category, agent_id, key, content, tags, timestamp, provenance FROM memories WHERE 1=1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if agent_id:
            query += " AND (agent_id = ? OR agent_id IS NULL)"
            params.append(agent_id)
        if key:
            query += " AND key = ?"
            params.append(key)
        query += " ORDER BY timestamp DESC"
        
        cursor = self._conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        items = []
        for r in rows:
            items.append(MemoryItem(
                id=r[0],
                category=r[1],
                agent_id=r[2],
                key=r[3],
                content=r[4],
                tags=json.loads(r[5]) if r[5] else [],
                timestamp=r[6],
                provenance=r[7]
            ))
        return items
    
    def search_semantic(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self._vector_index.search(query, top_k=top_k)
    
    def delete(self, memory_id: str) -> bool:
        with self._conn:
            cursor = self._conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            deleted = cursor.rowcount > 0
        if deleted:
            self._vector_index.remove(memory_id)
        return deleted
    
    def list_all(self, limit: int = 100) -> List[MemoryItem]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT id, category, agent_id, key, content, tags, timestamp, provenance FROM memories ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [
            MemoryItem(
                id=r[0],
                category=r[1],
                agent_id=r[2],
                key=r[3],
                content=r[4],
                tags=json.loads(r[5]) if r[5] else [],
                timestamp=r[6],
                provenance=r[7]
            ) for r in rows
        ]


# Global memory store instance
memory_store = MemoryStore()
