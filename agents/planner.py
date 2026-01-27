"""
Planner Agent - Designs yoga flow structure
"""
import json
from typing import Dict, List

from core.body_engine import BodyState
from prompts.planner_prompt import PROMPT_TEMPLATE


class PlannerAgent:
    """
    Planner Agent - designs the structure and rhythm of yoga sessions.
    Uses LLM to generate flow structure.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize Planner Agent.
        
        Args:
            llm_client: LLM client (OpenAI, Anthropic, etc.)
                       If None, will use a simple rule-based fallback
        """
        self.llm_client = llm_client
        self.prompt_template = PROMPT_TEMPLATE
    
    def generate_structure(self, body_state: BodyState, enriched_poses: List[Dict]) -> Dict:
        """
        Generate yoga flow structure.
        
        Args:
            body_state: BodyState object
            enriched_poses: List of enriched poses from RAG
        
        Returns:
            Dictionary with flow structure
        """
        if self.llm_client:
            return self._generate_with_llm(body_state, enriched_poses)
        else:
            return self._generate_rule_based(body_state)
    
    def _generate_with_llm(self, body_state: BodyState, enriched_poses: List[Dict]) -> Dict:
        """
        Generate structure using LLM (Groq, Gemini, Ollama).
        Falls back to rule-based on parse error or API failure.
        """
        from llm.client import extract_json

        prompt = self.prompt_template.format(
            cycle_phase=body_state.cycle_phase,
            intensity=body_state.intensity,
            duration_minutes=body_state.duration_minutes,
            allowed_pose_types=", ".join(body_state.allowed_pose_types),
            energy_level=body_state.energy_level,
            pain_level=body_state.pain_level,
            forbidden_pose_types=", ".join(body_state.forbidden_pose_types)
        )
        try:
            raw = self.llm_client.generate(
                prompt,
                system_prompt="You are a yoga flow planner. Reply with ONLY valid JSON, no markdown or extra text.",
                temperature=0.5,
            )
            text = extract_json(raw)
            out = json.loads(text)
            if isinstance(out, dict) and "structure" in out and isinstance(out["structure"], list):
                return out
        except Exception:
            pass
        return self._generate_rule_based(body_state)
    
    def _generate_rule_based(self, body_state: BodyState) -> Dict:
        """
        Rule-based structure generation (fallback when LLM not available).
        """
        duration = body_state.duration_minutes
        intensity = body_state.intensity
        phase = body_state.cycle_phase
        
        # Calculate time allocation
        if duration <= 15:
            breathing_time = 2
            main_time = duration - breathing_time - 3
            cool_down_time = 3
        elif duration <= 30:
            breathing_time = 3
            main_time = duration - breathing_time - 5
            cool_down_time = 5
        else:
            breathing_time = 5
            main_time = duration - breathing_time - 7
            cool_down_time = 7
        
        # Adjust based on intensity
        if intensity == "low":
            main_section_type = "gentle_flow"
        elif intensity == "high":
            main_section_type = "dynamic_flow"
        else:
            main_section_type = "moderate_flow"
        
        structure = {
            "structure": [
                {
                    "section": "breathing",
                    "minutes": breathing_time,
                    "description": "Centering and breath awareness to begin the practice"
                },
                {
                    "section": main_section_type,
                    "minutes": main_time,
                    "description": f"Main practice adapted for {phase} phase with {intensity} intensity"
                },
                {
                    "section": "cool_down",
                    "minutes": cool_down_time,
                    "description": "Restorative poses and gentle release"
                }
            ],
            "total_minutes": duration,
            "rationale": f"Designed for {phase} phase with {intensity} intensity, respecting energy level {body_state.energy_level}/5 and pain level {body_state.pain_level}/5"
        }
        
        return structure
