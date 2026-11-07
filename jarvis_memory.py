import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "jarvis_memory.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_key TEXT NOT NULL UNIQUE,
                fact_value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_message(role, content):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO conversations (role, content) VALUES (?, ?)",
            (role, content)
        )


def get_recent_messages(limit=20):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM conversations
            ORDER BY id DESC LIMIT ?
            """,
            (limit,)
        ).fetchall()

    return [
        {"role": role, "content": content}
        for role, content in reversed(rows)
    ]


def remember_fact(key, value):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO facts (fact_key, fact_value)
            VALUES (?, ?)
            ON CONFLICT(fact_key)
            DO UPDATE SET
                fact_value = excluded.fact_value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (key, value)
        )


def get_facts():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT fact_key, fact_value FROM facts"
        ).fetchall()

    return dict(rows)


initialize_database()