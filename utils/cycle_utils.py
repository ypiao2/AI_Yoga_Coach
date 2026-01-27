"""
Cycle utilities for calculating menstrual cycle phases
"""
from datetime import datetime, timedelta
from typing import Literal, Optional, Tuple


CyclePhase = Literal["menstrual", "follicular", "ovulation", "luteal"]


def calculate_cycle_phase(
    last_period_date: str,
    cycle_length: int = 28,
    current_date: Optional[str] = None
) -> Tuple[CyclePhase, int]:
    """
    Calculate current cycle phase based on last period date.
    
    Args:
        last_period_date: Date string in YYYY-MM-DD format
        cycle_length: Typical cycle length in days (default 28)
        current_date: Current date string (defaults to today)
    
    Returns:
        Tuple of (phase_name, day_in_cycle)
    """
    last_date = datetime.strptime(last_period_date, "%Y-%m-%d")
    current = datetime.strptime(current_date, "%Y-%m-%d") if current_date else datetime.now()
    
    days_since_period = (current - last_date).days
    
    # Normalize to current cycle
    day_in_cycle = days_since_period % cycle_length
    
    # Phase calculation (typical 28-day cycle)
    if day_in_cycle <= 5:
        phase = "menstrual"
    elif day_in_cycle <= 13:
        phase = "follicular"
    elif day_in_cycle <= 16:
        phase = "ovulation"
    else:
        phase = "luteal"
    
    return phase, day_in_cycle


def get_phase_intensity_guidance(phase: CyclePhase) -> dict:
    """
    Get intensity guidance for each cycle phase.
    
    Returns:
        Dictionary with intensity recommendations
    """
    guidance = {
        "menstrual": {
            "recommended_intensity": "low",
            "energy_level": "low",
            "focus": "restorative"
        },
        "follicular": {
            "recommended_intensity": "moderate_to_high",
            "energy_level": "increasing",
            "focus": "strength_building"
        },
        "ovulation": {
            "recommended_intensity": "high",
            "energy_level": "peak",
            "focus": "peak_performance"
        },
        "luteal": {
            "recommended_intensity": "moderate_to_low",
            "energy_level": "decreasing",
            "focus": "gentle_movement"
        }
    }
    return guidance.get(phase, guidance["menstrual"])
