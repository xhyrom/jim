from datetime import datetime
from typing import Any, Dict


def greeting_mapping(context: Dict[str, Any]) -> str:
    """Determine the appropriate greeting response based on context."""

    now = context.get("time", datetime.now().time())
    hour = now.hour

    if context.get("formal_mode", False):
        return "greeting.default"

    if 5 <= hour < 12:
        return "greeting.morning"
    elif 12 <= hour < 18:
        return "greeting.afternoon"
    else:
        return "greeting.evening"
