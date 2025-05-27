from datetime import datetime
from typing import Any, Dict


def get_time_mapping(context: Dict[str, Any]) -> str:
    """Determine the appropriate response template for get_time intent."""

    current_time = context.get("time", datetime.now().time())

    if context.get("formal_mode", False):
        return "get_time.formal"

    if current_time.hour < 12:
        return "get_time.morning"
    elif current_time.hour >= 18:
        return "get_time.evening"
    else:
        return "get_time.casual"


def get_date_mapping(context: Dict[str, Any]) -> str:
    """Determine the appropriate response template for get_date intent."""

    if not context.get("include_day_of_week", True):
        return "get_date.standard"
    else:
        return "get_date.with_day"
