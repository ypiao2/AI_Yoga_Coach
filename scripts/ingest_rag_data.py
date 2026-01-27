"""
RAG Data Ingestion Script
Import yoga knowledge into RAG vector store
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.vector_store import VectorStore
from rag.ingest import (
    ingest_from_json,
    ingest_from_knowledge_base,
    batch_ingest
)


def main():
    """Main ingestion function."""
    print("="*60)
    print("RAG Data Ingestion Tool")
    print("="*60)
    
    # Choose backend
    print("\nAvailable backends:")
    print("1. JSON (default, no setup required)")
    print("2. Pinecone (requires PINECONE_API_KEY)")
    print("3. ChromaDB (local, no API key needed)")
    print("4. Weaviate (requires WEAVIATE_URL)")
    
    choice = input("\nSelect backend (1-4, default=1): ").strip() or "1"
    
    backend_map = {
        "1": "json",
        "2": "pinecone",
        "3": "chroma",
        "4": "weaviate"
    }
    
    backend = backend_map.get(choice, "json")
    
    # Initialize vector store
    print(f"\nInitializing {backend} vector store...")
    vector_store = VectorStore(backend=backend)
    
    # Choose data source
    print("\nData sources:")
    print("1. From existing knowledge_base.py (default)")
    print("2. From JSON file")
    print("3. Batch from multiple sources")
    
    source_choice = input("\nSelect source (1-3, default=1): ").strip() or "1"
    
    if source_choice == "1":
        # Ingest from knowledge base
        print("\nIngesting from knowledge_base.py...")
        entries = ingest_from_knowledge_base(vector_store=vector_store)
        print(f"✅ Successfully ingested {len(entries)} entries")
    
    elif source_choice == "2":
        # Ingest from JSON
        json_path = input("Enter JSON file path: ").strip()
        if os.path.exists(json_path):
            entries = ingest_from_json(json_path, vector_store=vector_store)
            print(f"✅ Successfully ingested {len(entries)} entries")
        else:
            print(f"❌ File not found: {json_path}")
    
    elif source_choice == "3":
        # Batch ingest
        print("\nBatch ingestion example:")
        print("Create a JSON file with sources array:")
        print("""
        {
            "sources": [
                {"type": "knowledge_base"},
                {"type": "json", "path": "data/poses.json"}
            ]
        }
        """)
        config_path = input("Enter config JSON path (or press Enter to use default): ").strip()
        
        if not config_path:
            # Default: ingest from knowledge base
            entries = ingest_from_knowledge_base(vector_store=vector_store)
        else:
            import json
            with open(config_path, "r") as f:
                config = json.load(f)
            entries = batch_ingest(config.get("sources", []), vector_store=vector_store)
        
        print(f"✅ Successfully ingested {len(entries)} entries")
    
    # Test search
    print("\n" + "="*60)
    print("Testing search...")
    test_query = input("Enter a test query (or press Enter to skip): ").strip()
    
    if test_query:
        results = vector_store.search(test_query, top_k=3)
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('pose', 'Unknown')}")
            print(f"   Benefits: {', '.join(result.get('benefits', [])[:2])}")
    
    print("\n" + "="*60)
    print("✅ Ingestion complete!")


if __name__ == "__main__":
    main()
