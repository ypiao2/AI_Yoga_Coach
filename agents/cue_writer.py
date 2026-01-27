"""
Cue Writer Agent - Generates detailed cues for each pose
"""
import json
from typing import Dict, List

from core.body_engine import BodyState
from rag.knowledge_base import KnowledgeBase
from prompts.cue_writer_prompt import PROMPT_TEMPLATE


class CueWriterAgent:
    """
    Cue Writer Agent - generates detailed alignment cues and instructions.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize Cue Writer Agent.
        
        Args:
            llm_client: LLM client (OpenAI, Anthropic, etc.)
        """
        self.llm_client = llm_client
        self.prompt_template = PROMPT_TEMPLATE
        self.knowledge_base = KnowledgeBase()
    
    def generate_cues(
        self,
        sequence: Dict,
        body_state: BodyState
    ) -> Dict:
        """
        Generate cues for all poses in sequence.
        
        Args:
            sequence: Pose sequence from Sequencer Agent
            body_state: BodyState object
        
        Returns:
            Dictionary with cues for each pose
        """
        if self.llm_client:
            return self._generate_with_llm(sequence, body_state)
        else:
            return self._generate_rule_based(sequence, body_state)
    
    def _generate_with_llm(self, sequence: Dict, body_state: BodyState) -> Dict:
        """
        Generate cues using LLM (Groq, Gemini, Ollama).
        Falls back to rule-based on parse error or API failure.
        """
        from llm.client import extract_json

        pose_knowledge = {}
        for section in sequence.get("sequence", []):
            for pose_entry in section.get("poses", []):
                pose_name = pose_entry.get("pose")
                knowledge = self.knowledge_base.retrieve_by_pose(pose_name)
                if knowledge:
                    pose_knowledge[pose_name] = knowledge

        prompt = self.prompt_template.format(
            sequence=json.dumps(sequence, indent=2),
            pose_knowledge=json.dumps(pose_knowledge, indent=2),
            cycle_phase=body_state.cycle_phase,
            energy_level=body_state.energy_level
        )
        try:
            raw = self.llm_client.generate(
                prompt,
                system_prompt="You are a cue writer for yoga. Reply with ONLY valid JSON, no markdown or extra text.",
                temperature=0.5,
            )
            text = extract_json(raw)
            out = json.loads(text)
            if isinstance(out, dict) and "cues" in out and isinstance(out["cues"], list):
                return out
        except Exception:
            pass
        return self._generate_rule_based(sequence, body_state)
    
    def _generate_rule_based(self, sequence: Dict, body_state: BodyState) -> Dict:
        """
        Rule-based cue generation using knowledge base.
        """
        cues = []
        phase = body_state.cycle_phase
        
        # Tone mapping for cycle phases
        tone_map = {
            "menstrual": "gentle, nurturing, rest-focused",
            "follicular": "energizing, building",
            "ovulation": "confident, empowering",
            "luteal": "supportive, grounding"
        }
        tone = tone_map.get(phase, "supportive")
        
        for section in sequence.get("sequence", []):
            section_name = section.get("section")
            
            for pose_entry in section.get("poses", []):
                pose_name = pose_entry.get("pose")
                knowledge = self.knowledge_base.retrieve_by_pose(pose_name)
                
                if knowledge:
                    cue_entry = {
                        "pose": pose_name,
                        "section": section_name,
                        "alignment_cues": knowledge.get("alignment", []),
                        "breathing": knowledge.get("breathing", "Breathe deeply and steadily"),
                        "modifications": knowledge.get("modifications", ""),
                        "encouragement": self._generate_encouragement(pose_name, phase, tone)
                    }
                else:
                    # Fallback for poses without knowledge
                    cue_entry = {
                        "pose": pose_name,
                        "section": section_name,
                        "alignment_cues": ["Find a comfortable position", "Listen to your body"],
                        "breathing": "Breathe deeply and steadily",
                        "modifications": "",
                        "encouragement": f"Take your time in {pose_name}. Honor where you are today."
                    }
                
                cues.append(cue_entry)
        
        return {"cues": cues}
    
    def _generate_encouragement(self, pose_name: str, phase: str, tone: str) -> str:
        """Generate encouragement message based on phase and tone."""
        encouragements = {
            "menstrual": [
                "This is a beautiful resting pose. Allow yourself to fully relax here.",
                "Honor your body's need for rest today.",
                "There's no need to push. Simply be present."
            ],
            "follicular": [
                "Feel your strength building.",
                "Notice the energy flowing through your body.",
                "You're building toward your peak."
            ],
            "ovulation": [
                "Feel your power and grace.",
                "You're at your peak - embrace this strength.",
                "Move with confidence and ease."
            ],
            "luteal": [
                "Ground yourself here. You are supported.",
                "Gentle movement is medicine.",
                "Be kind to yourself in this pose."
            ]
        }
        
        phase_encouragements = encouragements.get(phase, encouragements["luteal"])
        import random
        return random.choice(phase_encouragements)
