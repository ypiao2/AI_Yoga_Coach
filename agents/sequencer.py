"""
Sequencer Agent - Selects and arranges specific poses
"""
import json
from typing import Dict, List

from core.body_engine import BodyState
from prompts.sequencer_prompt import PROMPT_TEMPLATE


class SequencerAgent:
    """
    Sequencer Agent - selects specific poses and arranges them in sequence.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize Sequencer Agent.
        
        Args:
            llm_client: LLM client (OpenAI, Anthropic, etc.)
        """
        self.llm_client = llm_client
        self.prompt_template = PROMPT_TEMPLATE
    
    def generate_sequence(
        self,
        structure: Dict,
        body_state: BodyState,
        enriched_poses: List[Dict]
    ) -> Dict:
        """
        Generate pose sequence from structure.
        
        Args:
            structure: Flow structure from Planner Agent
            body_state: BodyState object
            enriched_poses: List of enriched poses
        
        Returns:
            Dictionary with pose sequence
        """
        if self.llm_client:
            return self._generate_with_llm(structure, body_state, enriched_poses)
        else:
            return self._generate_rule_based(structure, body_state, enriched_poses)
    
    def _generate_with_llm(
        self,
        structure: Dict,
        body_state: BodyState,
        enriched_poses: List[Dict]
    ) -> Dict:
        """
        Generate sequence using LLM (Groq, Gemini, Ollama).
        Falls back to rule-based on parse error or API failure.
        """
        from llm.client import extract_json

        prompt = self.prompt_template.format(
            structure=json.dumps(structure, indent=2),
            enriched_poses=json.dumps(enriched_poses[:20], indent=2),
            cycle_phase=body_state.cycle_phase,
            intensity=body_state.intensity,
            duration_minutes=body_state.duration_minutes
        )
        try:
            raw = self.llm_client.generate(
                prompt,
                system_prompt="You are a yoga sequencer. Reply with ONLY valid JSON, no markdown or extra text.",
                temperature=0.5,
            )
            text = extract_json(raw)
            out = json.loads(text)
            if isinstance(out, dict) and "sequence" in out and isinstance(out["sequence"], list):
                return out
        except Exception:
            pass
        return self._generate_rule_based(structure, body_state, enriched_poses)
    
    def _generate_rule_based(
        self,
        structure: Dict,
        body_state: BodyState,
        enriched_poses: List[Dict]
    ) -> Dict:
        """
        Rule-based sequence generation.
        """
        sequence = []
        phase = body_state.cycle_phase
        intensity = body_state.intensity
        
        # Filter poses by phase and intensity
        suitable_poses = self._filter_poses_for_phase(enriched_poses, phase, intensity)
        
        for section in structure.get("structure", []):
            section_name = section.get("section")
            section_minutes = section.get("minutes", 5)
            
            if section_name == "breathing":
                poses = [
                    {
                        "pose": "breath_awareness",
                        "duration": f"{section_minutes} min",
                        "notes": "Focus on natural breathing, then deepen gradually"
                    }
                ]
            elif section_name in ["gentle_flow", "moderate_flow", "dynamic_flow"]:
                poses = self._select_main_poses(suitable_poses, section_minutes, intensity)
            elif section_name == "cool_down":
                poses = self._select_cool_down_poses(suitable_poses, section_minutes)
            else:
                poses = []
            
            sequence.append({
                "section": section_name,
                "poses": poses
            })
        
        return {
            "sequence": sequence,
            "total_estimated_minutes": structure.get("total_minutes", 20)
        }
    
    def _filter_poses_for_phase(
        self,
        poses: List[Dict],
        phase: str,
        intensity: str
    ) -> List[Dict]:
        """Filter poses suitable for cycle phase and intensity."""
        filtered = []
        
        for pose in poses:
            pose_types = pose.get("types", [])
            difficulty = pose.get("difficulty", "intermediate")
            
            # Phase-based filtering
            if phase == "menstrual":
                if any(pt in ["restorative", "gentle_stretch", "breathing", "forward_fold"] for pt in pose_types):
                    if intensity == "low" or difficulty == "beginner":
                        filtered.append(pose)
            elif phase == "ovulation":
                if intensity == "high":
                    filtered.append(pose)  # Most poses allowed
                else:
                    if difficulty != "advanced":
                        filtered.append(pose)
            else:  # follicular or luteal
                if difficulty != "advanced":
                    filtered.append(pose)
        
        return filtered if filtered else poses[:10]  # Fallback
    
    def _select_main_poses(
        self,
        poses: List[Dict],
        minutes: int,
        intensity: str
    ) -> List[Dict]:
        """Select poses for main flow section."""
        selected = []
        time_used = 0
        
        # Start with warm-up poses
        warm_up = [p for p in poses if "gentle_stretch" in p.get("types", [])]
        if warm_up:
            selected.append({
                "pose": warm_up[0].get("name"),
                "reps": 6,
                "notes": "Move with breath"
            })
            time_used += 2
        
        # Add main poses
        main_poses = [p for p in poses if p.get("name") not in [s.get("pose") for s in selected]]
        for pose in main_poses[:5]:  # Limit to 5 poses
            if time_used >= minutes - 2:
                break
            
            pose_name = pose.get("name")
            duration_suggestion = pose.get("duration_suggestion", "1 min")
            
            selected.append({
                "pose": pose_name,
                "duration": duration_suggestion,
                "notes": f"Hold or flow through {pose_name}"
            })
            time_used += 1
        
        return selected
    
    def _select_cool_down_poses(self, poses: List[Dict], minutes: int) -> List[Dict]:
        """Select poses for cool-down section."""
        cool_down_types = ["restorative", "gentle_stretch", "forward_fold"]
        cool_down_poses = [
            p for p in poses
            if any(pt in cool_down_types for pt in p.get("types", []))
        ]
        
        selected = []
        for pose in cool_down_poses[:3]:  # Limit to 3 poses
            selected.append({
                "pose": pose.get("name"),
                "duration": pose.get("duration_suggestion", "1 min"),
                "notes": "Rest and release"
            })
        
        return selected if selected else [
            {
                "pose": "child_pose",
                "duration": f"{minutes} min",
                "notes": "Final resting pose"
            }
        ]
