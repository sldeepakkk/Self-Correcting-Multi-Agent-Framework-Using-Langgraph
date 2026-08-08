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

# ── Reasoning Lessons ──────────────────────────────────
REASONING_SCHEMA = """
CREATE TABLE IF NOT EXISTS reasoning_lessons (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp           TEXT NOT NULL,
    query               TEXT NOT NULL,
    lesson              TEXT NOT NULL,
    defect_category     TEXT NOT NULL,
    applies_to          TEXT NOT NULL,
    confidence          REAL NOT NULL,
    active              INTEGER NOT NULL DEFAULT 1
);
"""

_reasoning_embedder = None

def _get_reasoning_embedder():
    global _reasoning_embedder
    if _reasoning_embedder is None:
        from sentence_transformers import SentenceTransformer
        from config import EMBEDDING_MODEL
        _reasoning_embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _reasoning_embedder


def _is_duplicate_reasoning_lesson(lesson_text: str, threshold: float = 0.9) -> bool:
    """Cosine similarity dedup — reuses the same embedder already loaded
    for the vector store/cache, no new dependency."""
    import numpy as np
    conn = _get_connection()
    conn.execute(REASONING_SCHEMA)
    rows = conn.execute("SELECT lesson FROM reasoning_lessons WHERE active = 1").fetchall()
    conn.close()
    if not rows:
        return False
    embedder = _get_reasoning_embedder()
    new_emb = embedder.encode([lesson_text], normalize_embeddings=True)[0]
    existing_embs = embedder.encode([r["lesson"] for r in rows], normalize_embeddings=True)
    sims = existing_embs @ new_emb
    return bool(np.max(sims) >= threshold)


def write_reasoning_lesson(query: str, lesson: str, defect_category: str, applies_to: str, confidence: float) -> dict:
    if _is_duplicate_reasoning_lesson(lesson):
        print(f"[REASONING MEMORY] Duplicate lesson (sim >= 0.9) — skipped")
        return {"active": 0, "status": "DUPLICATE_SKIPPED"}

    active = 1 if confidence >= REFLECTION_CONFIDENCE_MIN else 0
    status = "ACTIVE" if active else "QUARANTINED"
    timestamp = datetime.utcnow().isoformat()

    conn = _get_connection()
    conn.execute(REASONING_SCHEMA)
    cursor = conn.execute(
        """INSERT INTO reasoning_lessons
           (timestamp, query, lesson, defect_category, applies_to, confidence, active)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (timestamp, query, lesson, defect_category, applies_to, confidence, active)
    )
    conn.commit()
    lesson_id = cursor.lastrowid
    conn.close()

    print(f"[REASONING MEMORY] Lesson #{lesson_id} written — confidence={confidence:.2f} → {status}")

    # Append to human-readable MEMORY_LOG.md
    _append_memory_log(
        lesson_id=lesson_id,
        timestamp=timestamp,
        query=query,
        query_category=f"reasoning_{defect_category}",
        lesson=lesson,
        confidence=confidence,
        routing_recommendation=f"applies_to: {applies_to}",
        status=status
    )

    return {"id": lesson_id, "active": active, "status": status, "confidence": confidence, "lesson": lesson}


def load_reasoning_lessons(limit: int = 8) -> list[str]:
    """Recency-based for v1. Category column already present for a
    later top-N-per-category upgrade without a schema migration."""
    conn = _get_connection()
    conn.execute(REASONING_SCHEMA)
    rows = conn.execute(
        "SELECT lesson, defect_category FROM reasoning_lessons "
        "WHERE active = 1 ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [f"[{r['defect_category']}] {r['lesson']}" for r in rows]



# ── Load active lessons for planner priors ────────────────────────────────────

def load_lessons(limit: int = 10) -> list[str]:
    """
    Load active lessons above confidence threshold.
    Returns list of lesson strings loaded into planner and generator system prompts.
    Unifies reasoning lessons and general policy lessons.
    Most recent lessons first — recency bias is correct here.
    Only Gate 3-passing lessons (active=1) are returned.
    """
    conn = _get_connection()
    conn.execute(REASONING_SCHEMA)
    
    # 1. Load active reasoning lessons
    r_rows = conn.execute(
        """SELECT lesson, defect_category, applies_to, confidence
           FROM reasoning_lessons
           WHERE active = 1
           ORDER BY id DESC
           LIMIT ?""",
        (limit,)
    ).fetchall()

    # 2. Load active general lessons
    g_rows = conn.execute(
        """SELECT lesson, query_category, routing_recommendation, confidence
           FROM lessons
           WHERE active = 1
           ORDER BY id DESC
           LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()

    lessons = []
    for r in r_rows:
        lessons.append(
            f"[{r['defect_category']} | applies_to={r['applies_to']} | "
            f"confidence={r['confidence']:.2f}] {r['lesson']}"
        )
    for g in g_rows:
        lessons.append(
            f"[{g['query_category']} | {g['routing_recommendation']} | "
            f"confidence={g['confidence']:.2f}] {g['lesson']}"
        )

    lessons = lessons[:limit]
    if lessons:
        print(f"[EPISODIC MEMORY] Loaded {len(lessons)} active lessons")
    else:
        print("[EPISODIC MEMORY] No active lessons found")
    return lessons


# ── Inspection utilities ──────────────────────────────────────────────────────

def get_lesson_count() -> dict:
    """Returns lesson counts. Used by the Streamlit sidebar."""
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

    with open(MEMORY_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"[MEMORY LOG] Appended lesson #{lesson_id} to MEMORY_LOG.md")