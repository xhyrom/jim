from datetime import datetime
from typing import Any, Dict


def get_time(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    """
    Handle time inquiries

    intent: get_time
    """

    return {
        "data": {
            "time": datetime.now(),
            "timezone": "local",
        }
    }
