"""
RAG Retriever - Retrieves enriched pose information
v1.0: Simple retrieval from knowledge base
Future: Can integrate vector database for semantic search
"""
import logging
from typing import List, Dict
from .knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class RAGRetriever:
    """
    RAG Retriever for enriching pose candidates with knowledge.
    """
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
    
    def enrich_poses(
        self,
        pose_candidates: List[Dict],
        cycle_phase: str
    ) -> List[Dict]:
        """
        Enrich pose candidates with knowledge base information.
        
        Args:
            pose_candidates: List of pose dictionaries from pose pool
            cycle_phase: Current cycle phase
        
        Returns:
            List of enriched poses with alignment cues, contraindications, etc.
        """
        enriched = []
        
        for pose in pose_candidates:
            pose_name = pose.get("name")
            knowledge = self.knowledge_base.retrieve_by_pose(pose_name)
            
            enriched_pose = pose.copy()
            
            if knowledge:
                enriched_pose["alignment_cues"] = knowledge.get("alignment", [])
                enriched_pose["contraindications"] = knowledge.get("contraindications", [])
                enriched_pose["benefits"] = knowledge.get("benefits", [])
                enriched_pose["breathing_guidance"] = knowledge.get("breathing", "")
                enriched_pose["modifications"] = knowledge.get("modifications", "")
            else:
                # Default values if knowledge not found
                enriched_pose["alignment_cues"] = []
                enriched_pose["contraindications"] = []
                enriched_pose["benefits"] = []
                enriched_pose["breathing_guidance"] = "Breathe deeply and steadily"
                enriched_pose["modifications"] = ""
            
            enriched.append(enriched_pose)
        
        return enriched
    
    def search_for_chat(self, query: str, limit: int = 6) -> str:
        """
        Return relevant yoga knowledge as context for chat Q&A.
        Uses simple keyword overlap: entries that mention query words rank higher.
        """
        if not query or not query.strip():
            logger.info("[RAG] search_for_chat: empty query, no context")
            return ""
        words = set(q.lower() for q in query.strip().split() if len(q) > 1)
        if not words:
            logger.info("[RAG] search_for_chat: no query words (len>1), no context")
            return ""
        scored = []
        for e in self.knowledge_base.knowledge:
            pose = (e.get("pose") or "").lower().replace("_", " ")
            benefits = " ".join(e.get("benefits") or []).lower()
            alignment = " ".join(e.get("alignment") or []).lower()
            breathing = (e.get("breathing") or "").lower()
            modifications = (e.get("modifications") or "").lower()
            text = f"{pose} {benefits} {alignment} {breathing} {modifications}"
            hits = sum(1 for w in words if w in text)
            if hits > 0:
                scored.append((hits, e))
        scored.sort(key=lambda x: -x[0])
        chunks = []
        for _, e in scored[:limit]:
            pose = e.get("pose", "")
            parts = [f"**{pose}**"]
            if e.get("benefits"):
                parts.append("Benefits: " + "; ".join(e["benefits"][:3]))
            if e.get("alignment"):
                parts.append("Alignment: " + "; ".join(e["alignment"][:3]))
            if e.get("breathing"):
                parts.append("Breathing: " + e["breathing"])
            if e.get("contraindications"):
                parts.append("Avoid if: " + "; ".join(e["contraindications"][:2]))
            chunks.append("\n".join(parts))
        out = "\n\n".join(chunks) if chunks else ""
        if out:
            pose_ids = [e.get("pose", "") for _, e in scored[:limit]]
            logger.info("[RAG] search_for_chat: using RAG context, %d entries matched (poses/topics: %s)", len(pose_ids), pose_ids)
        else:
            logger.info("[RAG] search_for_chat: no RAG matches for query %r → LLM will use built-in/general knowledge only", query[:80])
        return out

    def get_safety_notes(self, pose_name: str, cycle_phase: str) -> Dict:
        """
        Get safety notes for a pose given cycle phase.
        
        Args:
            pose_name: Name of the pose
            cycle_phase: Current cycle phase
        
        Returns:
            Dictionary with safety notes
        """
        knowledge = self.knowledge_base.retrieve_by_pose(pose_name)
        
        if not knowledge:
            return {
                "contraindications": [],
                "cycle_specific_notes": ""
            }
        
        contraindications = knowledge.get("contraindications", [])
        
        # Cycle-specific safety notes
        cycle_notes = ""
        if cycle_phase == "menstrual":
            if "inversion" in pose_name or "headstand" in pose_name:
                cycle_notes = "Avoid inversions during menstrual phase"
        
        return {
            "contraindications": contraindications,
            "cycle_specific_notes": cycle_notes
        }
