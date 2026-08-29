"""
Lightweight SQLite-backed memory: stores conversation turns and
learned user preferences so the agent stays consistent across sessions.
"""
import sqlite3
import config


def _get_connection():
    conn = sqlite3.connect(config.MEMORY_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT,
            preference TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn


def log_message(user_id: str, role: str, content: str):
    """Save one chat turn (role = 'user' or 'assistant')."""
    conn = _get_connection()
    conn.execute(
        "INSERT INTO conversation_history (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content),
    )
    conn.commit()
    conn.close()


def get_recent_history(user_id: str, limit: int = 10) -> list[tuple[str, str]]:
    """Return the last `limit` (role, content) turns for this user, oldest first."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT role, content FROM conversation_history WHERE user_id = ? "
        "ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return list(reversed(rows))


def save_preference(user_id: str, preference: str):
    """Store a preference the agent extracted from the conversation."""
    conn = _get_connection()
    conn.execute(
        "INSERT INTO user_preferences (user_id, preference) VALUES (?, ?)",
        (user_id, preference),
    )
    conn.commit()
    conn.close()


def get_preferences(user_id: str) -> list[str]:
    """Return all stored preferences for this user."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT preference FROM user_preferences WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]
