"""
RAG Ingest - For importing yoga knowledge from external sources
Supports: Text, JSON, PDF, URLs. Saves to data/yoga_knowledge.json so the app uses it.
Long texts (e.g. ~100 A4 pages) are chunked and processed in passes, then merged.
"""
from typing import List, Dict, Optional
import json
import os
from pathlib import Path

from .vector_store import VectorStore
from .knowledge_io import save_knowledge_to_file, get_knowledge_path

# Max characters per LLM call; long docs are split into chunks of this size
CHUNK_CHARS = 90_000


def _chunk_text(text: str, size: int = CHUNK_CHARS) -> List[str]:
    """Split text into chunks of at most `size` chars, breaking at paragraph or line when possible."""
    if len(text) <= size:
        return [text] if text.strip() else []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        slice_ = text[start:end]
        # Prefer break at double newline (paragraph), then single newline
        if end < len(text):
            last_para = slice_.rfind("\n\n")
            last_line = slice_.rfind("\n")
            break_at = last_para if last_para > size // 2 else (last_line if last_line > size // 2 else -1)
            if break_at >= 0:
                slice_ = text[start : start + break_at + 1]
                end = start + break_at + 1
        chunks.append(slice_.strip())
        start = end
    return [c for c in chunks if c]


def ingest_from_json(
    json_path: str,
    vector_store: Optional[VectorStore] = None,
    save_to_rag: bool = True
) -> List[Dict]:
    """
    Ingest yoga knowledge from JSON file.
    
    Args:
        json_path: Path to JSON file
        vector_store: Optional vector store to save to
    
    Returns:
        List of structured knowledge entries
    
    Example JSON format:
    [
        {
            "pose": "child_pose",
            "alignment": ["..."],
            "contraindications": ["..."],
            "benefits": ["..."],
            "breathing": "...",
            "modifications": "..."
        }
    ]
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        entries = data if isinstance(data, list) else data.get("entries", [])
        
        if vector_store:
            for entry in entries:
                vector_store.add_knowledge(entry)
        if save_to_rag and entries:
            n = save_knowledge_to_file(entries, get_knowledge_path(), merge=True)
            print(f"✓ Saved {n} entries to RAG knowledge file")
        
        print(f"✓ Ingested {len(entries)} entries from {json_path}")
        return entries
    except Exception as e:
        print(f"Error ingesting from JSON: {e}")
        return []


def ingest_from_text(
    text: str,
    vector_store: Optional[VectorStore] = None,
    save_to_rag: bool = True,
    source_is_philosophy: bool = False
) -> List[Dict]:
    """
    Ingest yoga knowledge from text source (supports long texts, e.g. ~100 A4 pages).
    Uses LLM to extract structured knowledge (Groq, OpenAI, Anthropic). Long text is
    chunked automatically; all entries are merged and saved to data/yoga_knowledge.json.

    For 瑜伽经 / Yoga Sutras (philosophy, not asana): set source_is_philosophy=True.
    Entries will use "pose" as topic/sutra id and map teachings to benefits, breathing, etc.
    
    Args:
        text: Text content to ingest
        vector_store: Optional vector store to save to
        source_is_philosophy: If True, treat text as yoga philosophy (e.g. 瑜伽经), not physical asana
    
    Returns:
        List of structured knowledge entries
    """
    try:
        from config import Config
        
        def pick_extractor():
            extra = {"source_is_philosophy": source_is_philosophy}
            provider = (Config.LLM_PROVIDER or "").lower()
            # Respect LLM_PROVIDER so Groq is used when set (e.g. LLM_PROVIDER=groq + GROQ_API_KEY)
            if provider == "groq" and Config.GROQ_API_KEY:
                return lambda t, vs, sr: _extract_with_groq(t, vs, sr, **extra)
            if provider == "openai" and Config.OPENAI_API_KEY:
                return lambda t, vs, sr: _extract_with_openai(t, vs, sr, **extra)
            if provider == "anthropic" and Config.ANTHROPIC_API_KEY:
                return lambda t, vs, sr: _extract_with_anthropic(t, vs, sr, **extra)
            # Fallback: use first available key (same order as before)
            if Config.OPENAI_API_KEY:
                return lambda t, vs, sr: _extract_with_openai(t, vs, sr, **extra)
            if Config.ANTHROPIC_API_KEY:
                return lambda t, vs, sr: _extract_with_anthropic(t, vs, sr, **extra)
            if Config.GROQ_API_KEY:
                return lambda t, vs, sr: _extract_with_groq(t, vs, sr, **extra)
            return None
        
        extractor = pick_extractor()
        if not extractor:
            print("Warning: No LLM API key found (set GROQ_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY).")
            return []
        
        # Long text: chunk, extract per chunk, merge and save once
        if len(text.strip()) > CHUNK_CHARS:
            chunks = _chunk_text(text.strip(), CHUNK_CHARS)
            print(f"Long text ({len(text):,} chars) → {len(chunks)} chunks" + (" [philosophy]" if source_is_philosophy else ""))
            all_entries: List[Dict] = []
            seen_poses: set = set()  # dedupe by pose
            for i, chunk in enumerate(chunks):
                print(f"  Chunk {i + 1}/{len(chunks)} ({len(chunk):,} chars)...")
                entries = extractor(chunk, vector_store, save_to_rag=False)
                for e in entries:
                    if isinstance(e, dict) and e.get("pose") and e["pose"] not in seen_poses:
                        seen_poses.add(e["pose"])
                        all_entries.append(e)
            if save_to_rag and all_entries:
                n = save_knowledge_to_file(all_entries, get_knowledge_path(), merge=True)
                print(f"✓ Saved {n} entries from {len(chunks)} chunks")
            return all_entries
        
        return extractor(text, vector_store, save_to_rag)
    except Exception as e:
        print(f"Error ingesting from text: {e}")
        return []


def _extract_with_openai(
    text: str,
    vector_store: Optional[VectorStore],
    save_to_rag: bool = True,
    source_is_philosophy: bool = False
) -> List[Dict]:
    """Extract knowledge using OpenAI."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if source_is_philosophy:
            prompt = f"""The following text is yoga philosophy (瑜伽经 / Yoga Sutras), NOT physical asana. Extract by topic/sutra/chapter. Return a JSON array. Each entry: "pose" = topic id (e.g. sutra_1_1, sutra_samadhi), "alignment" = key concepts or [], "contraindications" = [], "benefits" = main teachings, "breathing" = pranayama/meditation where relevant, "modifications" = "".

Text:
{text}

Return only valid JSON array, no other text."""
        else:
            prompt = f"""Extract yoga pose knowledge from the following text and return as JSON array.
Each entry should have: pose, alignment (array), contraindications (array), benefits (array), breathing (string), modifications (string).

Text:
{text}

Return only valid JSON array, no other text."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        
        if vector_store:
            for entry in result:
                vector_store.add_knowledge(entry)
        if save_to_rag and result:
            n = save_knowledge_to_file(result, get_knowledge_path(), merge=True)
            print(f"✓ Saved {n} entries to RAG knowledge file")
        
        print(f"✓ Extracted {len(result)} entries using OpenAI")
        return result
    except Exception as e:
        print(f"Error extracting with OpenAI: {e}")
        return []


def _extract_with_anthropic(
    text: str,
    vector_store: Optional[VectorStore],
    save_to_rag: bool = True,
    source_is_philosophy: bool = False
) -> List[Dict]:
    """Extract knowledge using Anthropic."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        if source_is_philosophy:
            prompt = f"""The following text is yoga philosophy (瑜伽经 / Yoga Sutras), NOT physical asana. Extract by topic/sutra/chapter. Return a JSON array. Each entry: "pose" = topic id (e.g. sutra_1_1, sutra_samadhi), "alignment" = key concepts or [], "contraindications" = [], "benefits" = main teachings, "breathing" = pranayama/meditation where relevant, "modifications" = "".

Text:
{text}

Return only valid JSON array, no other text."""
        else:
            prompt = f"""Extract yoga pose knowledge from the following text and return as JSON array.
Each entry should have: pose, alignment (array), contraindications (array), benefits (array), breathing (string), modifications (string).

Text:
{text}

Return only valid JSON array, no other text."""
        
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = json.loads(response.content[0].text)
        
        if vector_store:
            for entry in result:
                vector_store.add_knowledge(entry)
        if save_to_rag and result:
            n = save_knowledge_to_file(result, get_knowledge_path(), merge=True)
            print(f"✓ Saved {n} entries to RAG knowledge file")
        
        print(f"✓ Extracted {len(result)} entries using Anthropic")
        return result
    except Exception as e:
        print(f"Error extracting with Anthropic: {e}")
        return []


def _extract_with_groq(
    text: str,
    vector_store: Optional[VectorStore],
    save_to_rag: bool = True,
    source_is_philosophy: bool = False
) -> List[Dict]:
    """Extract knowledge using Groq (uses llm.client)."""
    try:
        from llm.client import create_llm_client, extract_json
        
        client = create_llm_client()
        if not client:
            print("Warning: Groq client not available. Set GROQ_API_KEY and optionally LLM_PROVIDER=groq.")
            return []
        
        # Truncate if very long so we stay within context (Groq models have limits)
        max_chars = 120_000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[... text truncated for extraction ...]"
        
        if source_is_philosophy:
            system = """You are extracting from yoga philosophy (瑜伽经 / Yoga Sutras), NOT physical asana. 
Use "pose" as a topic/sutra id (e.g. sutra_1_1, sutra_samadhi, sutra_2_1). 
Put main teachings in "benefits", pranayama/meditation in "breathing", key concepts in "alignment". 
Use "contraindications" = [], "modifications" = "" where not applicable. 
Output only a JSON array of objects, no other text."""
            prompt = f"""The following is yoga philosophy (瑜伽经), not asana. Extract by topic/sutra. Return a JSON array. Each entry: "pose" (topic id, e.g. sutra_1_1), "alignment" (array, key concepts or []), "contraindications" ([]), "benefits" (array, main teachings), "breathing" (string, pranayama/meditation or ""), "modifications" ("").

Text:
{text}

Return only a valid JSON array, no markdown or extra text."""
        else:
            system = """You are a yoga knowledge extractor. Extract structured entries from the given text.
Use pose, alignment (array), contraindications (array), benefits (array), breathing (string), modifications (string).
Output only a JSON array of objects, no other text."""
            prompt = f"""Extract yoga-related knowledge from the following text. Return a JSON array of entries. Each entry must have: "pose" (string), "alignment" (array), "contraindications" (array), "benefits" (array), "breathing" (string), "modifications" (string). Use empty arrays/strings when not applicable.

Text:
{text}

Return only a valid JSON array, no markdown or extra text."""
        
        raw = client.generate(prompt, system_prompt=system, temperature=0.3)
        out = extract_json(raw)
        result = json.loads(out)
        if not isinstance(result, list):
            result = [result] if isinstance(result, dict) else []
        
        if vector_store:
            for entry in result:
                if isinstance(entry, dict) and entry.get("pose"):
                    vector_store.add_knowledge(entry)
        if save_to_rag and result:
            n = save_knowledge_to_file(result, get_knowledge_path(), merge=True)
            print(f"✓ Saved {n} entries to RAG knowledge file")
        
        print(f"✓ Extracted {len(result)} entries using Groq")
        return result
    except json.JSONDecodeError as e:
        print(f"Error parsing Groq JSON: {e}")
        return []
    except Exception as e:
        print(f"Error extracting with Groq: {e}")
        return []


def ingest_from_pdf(
    pdf_path: str,
    vector_store: Optional[VectorStore] = None,
    save_to_rag: bool = True,
    source_is_philosophy: bool = False
) -> List[Dict]:
    """
    Ingest yoga knowledge from PDF file (e.g. yoga book, 瑜伽经).
    Extracts text, uses LLM to get structured entries, then saves to RAG file.
    Set source_is_philosophy=True for 瑜伽经 / Yoga Sutras (philosophy, not asana).
    
    Args:
        pdf_path: Path to PDF file
        vector_store: Optional vector store to save to
        save_to_rag: If True, writes to data/yoga_knowledge.json (used by the app)
        source_is_philosophy: If True, treat as yoga philosophy (瑜伽经), not physical asana
    
    Returns:
        List of structured knowledge entries
    """
    try:
        import PyPDF2
        
        # Extract text from PDF
        text = ""
        with open(pdf_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return ingest_from_text(text, vector_store, save_to_rag=save_to_rag, source_is_philosophy=source_is_philosophy)
    except ImportError:
        print("Warning: PyPDF2 not installed. Install with: pip install PyPDF2")
        return []
    except Exception as e:
        print(f"Error ingesting from PDF: {e}")
        return []


def ingest_from_url(url: str, vector_store: Optional[VectorStore] = None) -> List[Dict]:
    """
    Ingest yoga knowledge from URL.
    
    Args:
        url: URL to fetch content from
        vector_store: Optional vector store to save to
    
    Returns:
        List of structured knowledge entries
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        
        return ingest_from_text(text, vector_store)
    except ImportError:
        print("Warning: requests or beautifulsoup4 not installed.")
        return []
    except Exception as e:
        print(f"Error ingesting from URL: {e}")
        return []


def ingest_from_knowledge_base(knowledge_base_path: str = None, vector_store: Optional[VectorStore] = None) -> List[Dict]:
    """
    Ingest from existing knowledge_base.py.
    
    Args:
        knowledge_base_path: Path to knowledge_base.py (default: rag/knowledge_base.py)
        vector_store: Optional vector store to save to
    
    Returns:
        List of structured knowledge entries
    """
    if knowledge_base_path is None:
        knowledge_base_path = Path(__file__).parent / "knowledge_base.py"
    
    try:
        from rag.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        entries = kb.get_all_knowledge()
        
        if vector_store:
            for entry in entries:
                vector_store.add_knowledge(entry)
        
        print(f"✓ Ingested {len(entries)} entries from knowledge base")
        return entries
    except Exception as e:
        print(f"Error ingesting from knowledge base: {e}")
        return []


def batch_ingest(
    sources: List[Dict],
    vector_store: Optional[VectorStore] = None
) -> List[Dict]:
    """
    Batch ingest from multiple sources.
    
    Args:
        sources: List of source dictionaries with 'type' and 'path'/'url'/'text'
        vector_store: Optional vector store to save to
    
    Example:
        sources = [
            {"type": "json", "path": "data/poses.json"},
            {"type": "url", "url": "https://example.com/yoga-guide"},
            {"type": "text", "text": "..."}
        ]
    
    Returns:
        List of all ingested entries
    """
    all_entries = []
    
    for source in sources:
        source_type = source.get("type")
        
        if source_type == "json":
            entries = ingest_from_json(source["path"], vector_store)
        elif source_type == "text":
            entries = ingest_from_text(source["text"], vector_store)
        elif source_type == "pdf":
            entries = ingest_from_pdf(source["path"], vector_store)
        elif source_type == "url":
            entries = ingest_from_url(source["url"], vector_store)
        elif source_type == "knowledge_base":
            entries = ingest_from_knowledge_base(source.get("path"), vector_store)
        else:
            print(f"Warning: Unknown source type: {source_type}")
            continue
        
        all_entries.extend(entries)
    
    print(f"✓ Batch ingested {len(all_entries)} total entries")
    return all_entries
