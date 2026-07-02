import sqlite3
import os
import json
from datetime import datetime
from config import (
    EPISODIC_MEMORY_DB,
    MEMORY_LOG_PATH,
    REFLECTION_CONFIDENCE_MIN
)


# ── Schema ────────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS lessons (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp               TEXT NOT NULL,
    query                   TEXT NOT NULL,
    query_category          TEXT NOT NULL,
    lesson                  TEXT NOT NULL,
    confidence              REAL NOT NULL,
    routing_recommendation  TEXT NOT NULL,
    active                  INTEGER NOT NULL DEFAULT 1,
    run_id                  TEXT
);
"""


def _get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(EPISODIC_MEMORY_DB), exist_ok=True)
    conn = sqlite3.connect(EPISODIC_MEMORY_DB)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    conn.commit()
    return conn


# ── Gate 3 — Write with confidence filtering ──────────────────────────────────

def write_lesson(
    query: str,
    query_category: str,
    lesson: str,
    confidence: float,
    routing_recommendation: str,
    run_id: str = None
) -> dict:
    """
    Gate 3 lives here.

    Confidence >= REFLECTION_CONFIDENCE_MIN → active=1 → loaded next run
    Confidence <  REFLECTION_CONFIDENCE_MIN → active=0 → quarantined

    Quarantined lessons are stored for inspection but never loaded
    into future system prompts. This prevents low-confidence noise
    from polluting the policy.

    Returns the written record including active status.
    """

    # Gate 3
    active = 1 if confidence >= REFLECTION_CONFIDENCE_MIN else 0
    status = "ACTIVE" if active else "QUARANTINED"

    timestamp = datetime.utcnow().isoformat()

    conn = _get_connection()
    cursor = conn.execute(
        """INSERT INTO lessons
           (timestamp, query, query_category, lesson, confidence,
            routing_recommendation, active, run_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (timestamp, query, query_category, lesson, confidence,
         routing_recommendation, active, run_id)
    )
    conn.commit()
    lesson_id = cursor.lastrowid
    conn.close()

    print(f"[EPISODIC MEMORY] Lesson #{lesson_id} written — "
          f"confidence={confidence:.2f} → {status}")

    # Append to human-readable MEMORY_LOG.md
    _append_memory_log(
        lesson_id=lesson_id,
        timestamp=timestamp,
        query=query,
        query_category=query_category,
        lesson=lesson,
        confidence=confidence,
        routing_recommendation=routing_recommendation,
        status=status
    )

    return {
        "id": lesson_id,
        "active": active,
        "status": status,
        "confidence": confidence,
        "lesson": lesson
    }


# ── Load active lessons for planner priors ────────────────────────────────────

def load_lessons(limit: int = 10) -> list[str]:
    """
    Load active lessons above confidence threshold.
    Returns list of lesson strings loaded into planner system prompt.
    Most recent lessons first — recency bias is correct here.
    Only Gate 3-passing lessons (active=1) are returned.
    """
    conn = _get_connection()
    rows = conn.execute(
        """SELECT lesson, query_category, routing_recommendation, confidence
           FROM lessons
           WHERE active = 1
           ORDER BY id DESC
           LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()

    if not rows:
        print("[EPISODIC MEMORY] No active lessons found")
        return []

    lessons = []
    for row in rows:
        lesson_str = (
            f"[{row['query_category']} | {row['routing_recommendation']} | "
            f"confidence={row['confidence']:.2f}] {row['lesson']}"
        )
        lessons.append(lesson_str)

    print(f"[EPISODIC MEMORY] Loaded {len(lessons)} active lessons")
    return lessons


# ── Inspection utilities ──────────────────────────────────────────────────────

def get_all_lessons(include_quarantined: bool = False) -> list[dict]:
    """
    Returns all lessons. Used for benchmarking and debugging.
    Set include_quarantined=True to see Gate 3 rejected lessons.
    """
    conn = _get_connection()
    if include_quarantined:
        rows = conn.execute(
            "SELECT * FROM lessons ORDER BY id DESC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM lessons WHERE active = 1 ORDER BY id DESC"
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_lesson_count() -> dict:
    """Returns counts for benchmarking."""
    conn = _get_connection()
    total = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    active = conn.execute(
        "SELECT COUNT(*) FROM lessons WHERE active = 1"
    ).fetchone()[0]
    quarantined = total - active
    conn.close()
    return {"total": total, "active": active, "quarantined": quarantined}


# ── MEMORY_LOG.md ─────────────────────────────────────────────────────────────

def _append_memory_log(
    lesson_id: int,
    timestamp: str,
    query: str,
    query_category: str,
    lesson: str,
    confidence: float,
    routing_recommendation: str,
    status: str
) -> None:
    """
    Appends a human-readable entry to MEMORY_LOG.md.
    This file is the GitHub artifact — people can read exactly
    what the system learned over N runs.
    Auto-creates the file with a header if it doesn't exist.
    """
    os.makedirs(os.path.dirname(MEMORY_LOG_PATH), exist_ok=True)

    # Create header if file doesn't exist
    if not os.path.exists(MEMORY_LOG_PATH):
        with open(MEMORY_LOG_PATH, "w") as f:
            f.write("# NSE Research Agent — Episodic Memory Log\n\n")
            f.write("Auto-generated by the reflector agent.\n")
            f.write("Each entry represents a lesson distilled from a "
                    "failure-and-recovery execution cycle.\n\n")
            f.write("---\n\n")

    entry = (
        f"### Lesson #{lesson_id} — {timestamp[:10]}\n"
        f"**Status:** {status} "
        f"(confidence={confidence:.2f}, threshold={REFLECTION_CONFIDENCE_MIN})\n\n"
        f"**Query:** {query}\n\n"
        f"**Category:** `{query_category}`\n\n"
        f"**Routing Recommendation:** `{routing_recommendation}`\n\n"
        f"**Lesson:**\n> {lesson}\n\n"
        f"---\n\n"
    )

    with open(MEMORY_LOG_PATH, "a") as f:
        f.write(entry)

    print(f"[MEMORY LOG] Appended lesson #{lesson_id} to MEMORY_LOG.md")