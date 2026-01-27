"""
Safety rules engine - deterministic rules for pose restrictions
"""
from typing import Literal, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .body_engine import BodyState


PoseType = Literal[
    "restorative",
    "gentle_stretch",
    "standing",
    "balance",
    "backbend",
    "forward_fold",
    "twist",
    "inversion",
    "arm_balance",
    "strong_core",
    "hip_opener",
    "breathing",
    "seated",      # e.g. lotus, hero; used for pranayama and meditation
    "side_bend",  # lateral lengthening
    "yin",        # long-held, passive; often menstrual/luteal safe
    "somatic",    # body-awareness, gentle release
    "mobility"    # CARs, rolling, prep
]


class SafetyRules:
    """
    Deterministic safety rules based on cycle phase and body state.
    This is NOT an LLM - it's rule-based logic.
    """
    
    @staticmethod
    def get_allowed_pose_types(state: "BodyState") -> List[PoseType]:
        """
        Determine allowed pose types based on body state.
        
        Returns:
            List of allowed pose types
        """
        allowed = []
        phase = state.cycle_phase
        energy = state.energy_level
        pain = state.pain_level
        
        # Base rules by cycle phase
        if phase == "menstrual":
            allowed.extend(["restorative", "gentle_stretch", "breathing", "forward_fold", "seated", "yin", "somatic", "mobility"])
            if energy <= 2:
                allowed.extend(["hip_opener"])
        elif phase == "follicular":
            allowed.extend([
                "standing", "balance", "gentle_stretch", "breathing",
                "hip_opener", "forward_fold", "twist", "seated", "side_bend", "yin", "somatic", "mobility"
            ])
            if energy >= 3:
                allowed.extend(["backbend", "arm_balance"])
        elif phase == "ovulation":
            allowed.extend([
                "standing", "balance", "backbend", "forward_fold",
                "twist", "arm_balance", "strong_core", "hip_opener",
                "breathing", "gentle_stretch", "seated", "side_bend", "yin", "somatic", "mobility"
            ])
            if energy >= 4:
                allowed.extend(["inversion"])
        elif phase == "luteal":
            allowed.extend([
                "gentle_stretch", "breathing", "forward_fold",
                "hip_opener", "twist", "restorative", "seated", "yin", "somatic", "mobility"
            ])
            if energy >= 3:
                allowed.extend(["standing", "balance", "side_bend"])
        
        # Pain-based restrictions
        if pain >= 4:
            # High pain - only very gentle poses
            allowed = [pt for pt in allowed if pt in [
                "restorative", "gentle_stretch", "breathing", "yin", "somatic", "mobility"
            ]]
        elif pain >= 3:
            # Moderate pain - avoid intense poses
            allowed = [pt for pt in allowed if pt not in [
                "inversion", "arm_balance", "strong_core", "backbend"
            ]]
        
        # Energy-based restrictions
        if energy <= 1:
            # Very low energy - only restorative
            allowed = ["restorative", "breathing"]
        elif energy <= 2:
            # Low energy - remove intense poses
            allowed = [pt for pt in allowed if pt not in [
                "inversion", "arm_balance", "strong_core"
            ]]
        
        # Remove duplicates and return
        return list(set(allowed))
    
    @staticmethod
    def get_forbidden_pose_types(state: "BodyState") -> List[PoseType]:
        """
        Get explicitly forbidden pose types.
        
        Returns:
            List of forbidden pose types
        """
        all_types: List[PoseType] = [
            "restorative", "gentle_stretch", "standing", "balance",
            "backbend", "forward_fold", "twist", "inversion",
            "arm_balance", "strong_core", "hip_opener", "breathing",
            "seated", "side_bend", "yin", "somatic", "mobility"
        ]
        allowed = SafetyRules.get_allowed_pose_types(state)
        return [pt for pt in all_types if pt not in allowed]
    
    @staticmethod
    def get_intensity_level(state: "BodyState") -> Literal["low", "moderate", "high"]:
        """
        Determine overall intensity level for the session.
        
        Returns:
            Intensity level string
        """
        phase = state.cycle_phase
        energy = state.energy_level
        pain = state.pain_level
        
        # Pain overrides everything
        if pain >= 4:
            return "low"
        if pain >= 3:
            return "low"
        
        # Energy-based intensity
        if energy <= 1:
            return "low"
        if energy <= 2:
            return "low"
        
        # Phase-based intensity
        if phase == "menstrual":
            return "low"
        elif phase == "ovulation" and energy >= 4:
            return "high"
        elif phase == "follicular" and energy >= 3:
            return "moderate"
        elif phase == "luteal":
            return "low" if energy <= 2 else "moderate"
        
        return "moderate"
