"""
Body State Engine - Core deterministic logic for body state calculation
This is the "hardcore" part of the system - NOT an LLM.
"""
from dataclasses import dataclass
from typing import Literal, List
from datetime import datetime

from utils.cycle_utils import calculate_cycle_phase, CyclePhase
from .safety_rules import SafetyRules, PoseType


@dataclass
class BodyState:
    """Body state representation"""
    cycle_phase: CyclePhase
    day_in_cycle: int
    energy_level: int  # 1-5 scale
    pain_level: int    # 1-5 scale
    duration_minutes: int
    intensity: Literal["low", "moderate", "high"]
    allowed_pose_types: List[PoseType]
    forbidden_pose_types: List[PoseType]
    last_period_date: str
    cycle_length: int
    training_focus: List[PoseType]  # e.g. seated, forward_fold, backbend, twist, side_bend, balance, inversion


class BodyStateEngine:
    """
    Body State Engine - calculates body state and safety constraints.
    
    This is deterministic AI, not LLM-based.
    """
    
    def __init__(self):
        self.safety_rules = SafetyRules()
    
    def process(self, user_input: dict) -> BodyState:
        """
        Process user input and generate body state.
        
        Input format:
        {
            "last_period_date": "2026-01-20",
            "cycle_length": 28,
            "energy": 2,
            "pain": 3,
            "duration": 20
        }
        
        Returns:
            BodyState object with all calculated fields
        """
        # Extract inputs
        last_period_date = user_input.get("last_period_date")
        cycle_length = user_input.get("cycle_length", 28)
        energy = user_input.get("energy", 3)
        pain = user_input.get("pain", 1)
        duration = user_input.get("duration", 20)
        
        # Validate inputs
        if not last_period_date:
            raise ValueError("last_period_date is required")
        
        # Calculate cycle phase
        cycle_phase, day_in_cycle = calculate_cycle_phase(
            last_period_date,
            cycle_length
        )
        
        # Resolve training_focus: valid internal types for targeted practice
        valid_focus = {"seated", "forward_fold", "backbend", "twist", "side_bend", "balance", "inversion"}
        raw_focus = user_input.get("training_focus") or []
        training_focus = [t for t in raw_focus if t in valid_focus]
        
        # Create initial state
        state = BodyState(
            cycle_phase=cycle_phase,
            day_in_cycle=day_in_cycle,
            energy_level=energy,
            pain_level=pain,
            duration_minutes=duration,
            intensity="moderate",  # Will be calculated
            allowed_pose_types=[],
            forbidden_pose_types=[],
            last_period_date=last_period_date,
            cycle_length=cycle_length,
            training_focus=training_focus
        )
        
        # Apply safety rules
        state.allowed_pose_types = self.safety_rules.get_allowed_pose_types(state)
        state.forbidden_pose_types = self.safety_rules.get_forbidden_pose_types(state)
        state.intensity = self.safety_rules.get_intensity_level(state)
        
        # If user chose training focus: keep only allowed types that are in focus.
        # If intersection is empty (e.g. only inversion but phase disallows it), ignore focus and use full allowed so a flow can still be generated.
        if training_focus:
            focused = [t for t in state.allowed_pose_types if t in training_focus]
            if focused:
                state.allowed_pose_types = focused
        
        return state
    
    def to_dict(self, state: BodyState) -> dict:
        """
        Convert BodyState to dictionary for API responses.
        
        Returns:
            Dictionary representation of body state
        """
        return {
            "cycle_phase": state.cycle_phase,
            "day_in_cycle": state.day_in_cycle,
            "intensity": state.intensity,
            "allowed_pose_types": state.allowed_pose_types,
            "forbidden_pose_types": state.forbidden_pose_types,
            "energy_level": state.energy_level,
            "pain_level": state.pain_level,
            "duration_minutes": state.duration_minutes,
            "training_focus": state.training_focus
        }
