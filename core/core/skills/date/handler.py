import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional


def ordinal_suffix(day: int) -> str:
    """Return the ordinal suffix for a day number (1st, 2nd, 3rd, etc.)"""
    if 11 <= day <= 13:
        return "th"

    remainder = day % 10
    if remainder == 1:
        return "st"
    elif remainder == 2:
        return "nd"
    elif remainder == 3:
        return "rd"
    else:
        return "th"


def format_date_for_speech(date_obj: date) -> str:
    """Format a date in a natural, speech-friendly way"""
    month = date_obj.strftime("%B")
    day = date_obj.day
    year = date_obj.year

    day_with_suffix = f"{day}{ordinal_suffix(day)}"

    return f"{month} {day_with_suffix}, {year}"


def parse_date_string(date_str: str) -> Optional[date]:
    """Parse a date string in various formats"""
    formats = [
        "%Y-%m-%d",  # 2025-06-05
        "%m/%d/%Y",  # 06/05/2025
        "%d/%m/%Y",  # 05/06/2025
        "%B %d, %Y",  # June 5, 2025
        "%b %d, %Y",  # Jun 5, 2025
        "%d %B %Y",  # 5 June 2025
        "%d %b %Y",  # 5 Jun 2025
        "%B %d %Y",  # June 5 2025
        "%b %d %Y",  # Jun 5 2025
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


async def get_date(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    """
    Handle date inquiries

    intent: get_date
    """
    # Default to current date
    target_date = datetime.now().date()
    is_specific_date = False
    original_date_str = None

    # Check for date entity
    if "date" in entities and entities["date"]:
        date_entity = entities["date"][0]["value"]

        # Handle relative dates
        if date_entity.get("type") == "relative":
            relative = date_entity.get("relative", "today").lower()

            if relative == "tomorrow":
                target_date = target_date + timedelta(days=1)
            elif relative == "yesterday":
                target_date = target_date - timedelta(days=-1)
            # Handle "next Monday", "last Friday", etc.
            elif "next" in relative or "last" in relative:
                # This would require more complex parsing
                pass

        # Handle specific date
        elif "date" in date_entity:
            date_str = date_entity.get("date")
            original_date_str = date_str
            parsed_date = parse_date_string(date_str)

            if parsed_date:
                target_date = parsed_date
                is_specific_date = True

    # Check for raw date in text
    elif "text" in context:
        text = context.get("text", "")

        # Look for YYYY-MM-DD pattern
        date_matches = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        if date_matches:
            original_date_str = date_matches[0]
            parsed_date = parse_date_string(original_date_str)
            if parsed_date:
                target_date = parsed_date
                is_specific_date = True

        # Look for MM/DD/YYYY pattern
        if not is_specific_date:
            date_matches = re.findall(r"\b(\d{1,2}/\d{1,2}/\d{4})\b", text)
            if date_matches:
                original_date_str = date_matches[0]
                parsed_date = parse_date_string(original_date_str)
                if parsed_date:
                    target_date = parsed_date
                    is_specific_date = True

    # Format date for speech
    formatted_date = format_date_for_speech(target_date)

    # Get day of week
    day_of_week = target_date.strftime("%A")

    # Calculate days from today
    today = datetime.now().date()
    days_difference = (target_date - today).days

    relative_description = ""
    if days_difference == 0:
        relative_description = "today"
    elif days_difference == 1:
        relative_description = "tomorrow"
    elif days_difference == -1:
        relative_description = "yesterday"
    elif 1 < days_difference <= 7:
        relative_description = f"{days_difference} days from now"
    elif -7 <= days_difference < -1:
        relative_description = f"{abs(days_difference)} days ago"

    return {
        "data": {
            "date": target_date,
            "formatted_date": formatted_date,
            "day_of_week": day_of_week,
            "is_specific_date": is_specific_date,
            "original_date_str": original_date_str,
            "is_today": days_difference == 0,
            "is_future": days_difference > 0,
            "is_past": days_difference < 0,
            "days_from_today": days_difference,
            "relative_description": relative_description,
            "timezone": "local",
        }
    }
