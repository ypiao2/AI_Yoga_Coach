"""
Time utilities for yoga flow generation
"""
from datetime import datetime, timedelta
from typing import Tuple


def parse_duration(duration_str: str) -> int:
    """
    Parse duration string to minutes.
    
    Examples:
        "20 min" -> 20
        "1 hour" -> 60
        "30" -> 30
    
    Args:
        duration_str: Duration string
    
    Returns:
        Duration in minutes
    """
    duration_str = duration_str.lower().strip()
    
    if "hour" in duration_str or "hr" in duration_str:
        hours = float(duration_str.split()[0])
        return int(hours * 60)
    elif "min" in duration_str:
        minutes = float(duration_str.split()[0])
        return int(minutes)
    else:
        # Assume minutes if no unit specified
        try:
            return int(float(duration_str))
        except ValueError:
            return 20  # Default


def format_duration(minutes: int) -> str:
    """
    Format minutes to human-readable string.
    
    Args:
        minutes: Duration in minutes
    
    Returns:
        Formatted string (e.g., "20 min", "1 hour 15 min")
    """
    if minutes < 60:
        return f"{minutes} min"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} min"


def calculate_time_allocation(
    total_minutes: int,
    sections: list[str]
) -> dict[str, int]:
    """
    Calculate time allocation for different sections.
    
    Args:
        total_minutes: Total session duration
        sections: List of section names
    
    Returns:
        Dictionary mapping section names to allocated minutes
    """
    num_sections = len(sections)
    if num_sections == 0:
        return {}
    
    base_time = total_minutes // num_sections
    remainder = total_minutes % num_sections
    
    allocation = {}
    for i, section in enumerate(sections):
        allocation[section] = base_time + (1 if i < remainder else 0)
    
    return allocation
