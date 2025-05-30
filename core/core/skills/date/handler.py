from datetime import datetime
from typing import Any, Dict


async def get_date(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    """
    Handle date inquiries

    intent: get_date
    """

    time = datetime.now()

    return {
        "data": {
            "date": time.date(),
            "day_of_week": time.strftime("%A"),
            "timezone": "local",
        }
    }
