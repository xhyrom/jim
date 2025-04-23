from typing import Dict, Any
from datetime import datetime


def get_time(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    current_time = datetime.now().strftime("%I:%M %p")

    return {
        "response": f"It's currently {current_time}.",
        "data": {"time": current_time},
    }
