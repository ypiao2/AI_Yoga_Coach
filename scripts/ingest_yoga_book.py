#!/usr/bin/env python3
"""
Ingest yoga books/texts into the RAG knowledge DB.

Usage:
  # 瑜伽经 / Yoga Sutras (philosophy, NOT asana) — use --philosophy
  python scripts/ingest_yoga_book.py --philosophy data/yoga_sutras.txt

  # From a text file (asana/pose content; long texts chunked automatically)
  python scripts/ingest_yoga_book.py path/to/my_knowledge.txt

  # From a PDF (add --philosophy for 瑜伽经)
  python scripts/ingest_yoga_book.py --philosophy path/to/book.pdf

  # From a JSON file (no API key needed)
  python scripts/ingest_yoga_book.py path/to/poses.json

Entries are merged into data/yoga_knowledge.json. The app uses that file on startup.
For .txt /.md /.pdf: set GROQ_API_KEY (or OPENAI_API_KEY / ANTHROPIC_API_KEY) in .env.
"""
import sys
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Load .env so GROQ_API_KEY etc. are available for text/PDF extraction
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    pass


def main():
    import os
    os.chdir(ROOT)  # so data/yoga_knowledge.json is under project root

    argv = [a for a in sys.argv[1:] if a != "--philosophy"]
    philosophy = "--philosophy" in sys.argv

    if len(argv) < 1:
        print(__doc__)
        print("Example: python scripts/ingest_yoga_book.py --philosophy data/yoga_sutras.txt")
        sys.exit(1)

    src = Path(argv[0])
    if not src.exists():
        print(f"File not found: {src}")
        sys.exit(1)

    suff = src.suffix.lower()
    entries = []

    if suff == ".pdf":
        from rag.ingest import ingest_from_pdf
        entries = ingest_from_pdf(str(src), save_to_rag=True, source_is_philosophy=philosophy)
        if not entries:
            print("No entries extracted. Set GROQ_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY for PDF.")
    elif suff == ".json":
        from rag.ingest import ingest_from_json
        entries = ingest_from_json(str(src), save_to_rag=True)
    elif suff in (".txt", ".md"):
        from rag.ingest import ingest_from_text
        text = src.read_text(encoding="utf-8", errors="replace")
        entries = ingest_from_text(text, save_to_rag=True, source_is_philosophy=philosophy)
        if not entries:
            print("No entries extracted. Set GROQ_API_KEY (or OPENAI/ANTHROPIC) for text extraction.")
    else:
        print("Use a .pdf, .txt, .md, or .json file.")
        sys.exit(1)

    if philosophy:
        print("(Ingested as yoga philosophy / 瑜伽经 — topic/sutra entries, not asana.)")
    print(f"Done. Ingested {len(entries)} entries into RAG. Restart the app to use them.")


if __name__ == "__main__":
    main()
