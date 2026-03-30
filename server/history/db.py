import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).parent / "chat_history.db"

class Database:
  def __init__(self):
    with sqlite3.connect(DB_PATH) as conn:
      conn.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            messages TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      """)
      conn.commit()

  def save_thread(self, thread_id: str, session_id: str, messages: list):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO threads (id, session_id, messages)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET messages = excluded.messages
        """, (thread_id, session_id, json.dumps(messages)))
        conn.commit()

  def get_thread_messages(self, thread_id: str) -> list:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT messages FROM threads WHERE id = ?", (thread_id,)
        )
        row = cursor.fetchone()
        return json.loads(row[0]) if row else []

  def get_session_threads(self, session_id: str) -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT id, created_at FROM threads WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,)
        )
        return [{"id": row[0], "created_at": row[1]} for row in cursor.fetchall()]

db = Database()