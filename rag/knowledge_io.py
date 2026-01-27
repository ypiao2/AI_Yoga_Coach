"""
Load/save yoga knowledge from the RAG knowledge file.
The app's KnowledgeBase loads from this file so ingested books are used automatically.
"""
import json
import os
from pathlib import Path
from typing import List, Dict

DEFAULT_KNOWLEDGE_FILE = "data/yoga_knowledge.json"


def get_knowledge_path() -> Path:
    """Path to the knowledge JSON file used by RAG."""
    path = os.getenv("RAG_KNOWLEDGE_FILE", DEFAULT_KNOWLEDGE_FILE)
    return Path(path)


def load_knowledge_from_file(path: Path = None) -> List[Dict]:
    """
    Load knowledge entries from JSON file.
    Returns [] if file does not exist or is invalid.
    """
    p = path or get_knowledge_path()
    if not p.exists():
        return []
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else data.get("entries", [])
    except Exception:
        return []


def save_knowledge_to_file(
    entries: List[Dict],
    path: Path = None,
    merge: bool = True
) -> int:
    """
    Save knowledge entries to JSON file.
    If merge=True and file exists, new entries overwrite/add by pose name.
    Creates parent dirs if needed. Returns number of entries written.
    """
    p = path or get_knowledge_path()
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)

    if merge and p.exists():
        existing = {e.get("pose"): e for e in load_knowledge_from_file(p) if e.get("pose")}
        for e in entries:
            if e.get("pose"):
                existing[e["pose"]] = e
        entries = list(existing.values())

    with open(p, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    return len(entries)
