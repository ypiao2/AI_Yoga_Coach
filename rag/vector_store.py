"""
Vector Store for RAG - Supports multiple vector database backends
"""
from typing import List, Dict, Optional
import json
import os

from config import Config


class VectorStore:
    """
    Vector store abstraction for RAG.
    Supports: Pinecone, Weaviate, ChromaDB, or simple JSON storage.
    """
    
    def __init__(self, backend: str = "json"):
        """
        Initialize vector store.
        
        Args:
            backend: Backend type ("pinecone", "weaviate", "chroma", "json")
        """
        self.backend = backend
        self.store = None
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the selected backend."""
        if self.backend == "pinecone":
            self._init_pinecone()
        elif self.backend == "weaviate":
            self._init_weaviate()
        elif self.backend == "chroma":
            self._init_chroma()
        elif self.backend == "json":
            self._init_json()
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
    
    def _init_pinecone(self):
        """Initialize Pinecone backend."""
        try:
            import pinecone
            api_key = os.getenv("PINECONE_API_KEY")
            environment = os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp")
            
            if not api_key:
                print("Warning: PINECONE_API_KEY not set. Using JSON backend.")
                self.backend = "json"
                self._init_json()
                return
            
            pinecone.init(api_key=api_key, environment=environment)
            index_name = os.getenv("PINECONE_INDEX_NAME", "yoga-knowledge")
            
            # Create index if it doesn't exist
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
            
            self.store = pinecone.Index(index_name)
            print("✓ Pinecone vector store initialized")
        except ImportError:
            print("Warning: pinecone-client not installed. Using JSON backend.")
            self.backend = "json"
            self._init_json()
        except Exception as e:
            print(f"Warning: Failed to initialize Pinecone: {e}. Using JSON backend.")
            self.backend = "json"
            self._init_json()
    
    def _init_weaviate(self):
        """Initialize Weaviate backend."""
        try:
            import weaviate
            url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
            api_key = os.getenv("WEAVIATE_API_KEY")
            
            if api_key:
                auth = weaviate.AuthApiKey(api_key=api_key)
                self.store = weaviate.Client(url=url, auth_client_secret=auth)
            else:
                self.store = weaviate.Client(url=url)
            
            print("✓ Weaviate vector store initialized")
        except ImportError:
            print("Warning: weaviate-client not installed. Using JSON backend.")
            self.backend = "json"
            self._init_json()
        except Exception as e:
            print(f"Warning: Failed to initialize Weaviate: {e}. Using JSON backend.")
            self.backend = "json"
            self._init_json()
    
    def _init_chroma(self):
        """Initialize ChromaDB backend."""
        try:
            import chromadb
            persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
            self.store = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.store.get_or_create_collection(
                name="yoga_knowledge",
                metadata={"description": "Yoga pose knowledge base"}
            )
            print("✓ ChromaDB vector store initialized")
        except ImportError:
            print("Warning: chromadb not installed. Using JSON backend.")
            self.backend = "json"
            self._init_json()
        except Exception as e:
            print(f"Warning: Failed to initialize ChromaDB: {e}. Using JSON backend.")
            self.backend = "json"
            self._init_json()
    
    def _init_json(self):
        """Initialize simple JSON file backend."""
        self.json_path = os.getenv("RAG_JSON_PATH", "./rag/knowledge_db.json")
        os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
        
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                self.store = json.load(f)
        else:
            self.store = {"entries": []}
        
        print("✓ JSON vector store initialized")
    
    def add_knowledge(self, knowledge_entry: Dict, embedding: Optional[List[float]] = None):
        """
        Add knowledge entry to vector store.
        
        Args:
            knowledge_entry: Dictionary with pose knowledge
            embedding: Optional embedding vector
        """
        if self.backend == "pinecone":
            self._add_to_pinecone(knowledge_entry, embedding)
        elif self.backend == "weaviate":
            self._add_to_weaviate(knowledge_entry, embedding)
        elif self.backend == "chroma":
            self._add_to_chroma(knowledge_entry, embedding)
        else:  # json
            self._add_to_json(knowledge_entry)
    
    def _add_to_pinecone(self, entry: Dict, embedding: Optional[List[float]]):
        """Add to Pinecone."""
        if not embedding:
            print("Warning: No embedding provided for Pinecone. Skipping.")
            return
        
        pose_name = entry.get("pose", "unknown")
        metadata = {
            "pose": pose_name,
            "alignment": json.dumps(entry.get("alignment", [])),
            "contraindications": json.dumps(entry.get("contraindications", [])),
            "benefits": json.dumps(entry.get("benefits", [])),
            "breathing": entry.get("breathing", ""),
            "modifications": entry.get("modifications", "")
        }
        
        self.store.upsert([(pose_name, embedding, metadata)])
    
    def _add_to_weaviate(self, entry: Dict, embedding: Optional[List[float]]):
        """Add to Weaviate."""
        # Implementation for Weaviate
        pass
    
    def _add_to_chroma(self, entry: Dict, embedding: Optional[List[float]]):
        """Add to ChromaDB."""
        pose_name = entry.get("pose", "unknown")
        document = json.dumps(entry)
        
        if embedding:
            self.collection.add(
                ids=[pose_name],
                embeddings=[embedding],
                documents=[document],
                metadatas=[{"pose": pose_name}]
            )
        else:
            self.collection.add(
                ids=[pose_name],
                documents=[document],
                metadatas=[{"pose": pose_name}]
            )
    
    def _add_to_json(self, entry: Dict):
        """Add to JSON file."""
        self.store["entries"].append(entry)
        self._save_json()
    
    def _save_json(self):
        """Save JSON store to file."""
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.store, f, indent=2, ensure_ascii=False)
    
    def search(self, query: str, top_k: int = 5, embedding: Optional[List[float]] = None) -> List[Dict]:
        """
        Search knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results to return
            embedding: Optional query embedding
        
        Returns:
            List of matching knowledge entries
        """
        if self.backend == "pinecone":
            return self._search_pinecone(query, top_k, embedding)
        elif self.backend == "weaviate":
            return self._search_weaviate(query, top_k, embedding)
        elif self.backend == "chroma":
            return self._search_chroma(query, top_k, embedding)
        else:  # json
            return self._search_json(query, top_k)
    
    def _search_pinecone(self, query: str, top_k: int, embedding: Optional[List[float]]) -> List[Dict]:
        """Search Pinecone."""
        if not embedding:
            return []
        
        results = self.store.query(embedding, top_k=top_k, include_metadata=True)
        return [r["metadata"] for r in results.get("matches", [])]
    
    def _search_weaviate(self, query: str, top_k: int, embedding: Optional[List[float]]) -> List[Dict]:
        """Search Weaviate."""
        # Implementation for Weaviate
        return []
    
    def _search_chroma(self, query: str, top_k: int, embedding: Optional[List[float]]) -> List[Dict]:
        """Search ChromaDB."""
        if embedding:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=top_k
            )
        else:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
        
        entries = []
        for i, doc in enumerate(results.get("documents", [[]])[0]):
            entries.append(json.loads(doc))
        return entries
    
    def _search_json(self, query: str, top_k: int) -> List[Dict]:
        """Simple text search in JSON."""
        query_lower = query.lower()
        matches = []
        
        for entry in self.store.get("entries", []):
            score = 0
            pose_name = entry.get("pose", "").lower()
            benefits = " ".join(entry.get("benefits", [])).lower()
            breathing = entry.get("breathing", "").lower()
            
            if query_lower in pose_name:
                score += 3
            if query_lower in benefits:
                score += 2
            if query_lower in breathing:
                score += 1
            
            if score > 0:
                matches.append((score, entry))
        
        matches.sort(reverse=True, key=lambda x: x[0])
        return [entry for _, entry in matches[:top_k]]
