import re
from datetime import datetime, time
from typing import Any, Dict, Optional


def format_time_for_speech(time_obj: time) -> str:
    """Format a time in a natural, speech-friendly way"""
    # Get hours and minutes
    hour = time_obj.hour
    minute = time_obj.minute

    # Convert to 12-hour format
    period = "AM" if hour < 12 else "PM"
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12

    # Different formats based on minutes
    if minute == 0:
        return f"{hour_12} {period}"
    elif minute < 10:
        return f"{hour_12} oh {minute} {period}"
    else:
        return f"{hour_12} {minute} {period}"


def format_time_words(time_obj: time) -> str:
    """Format time in words (like 'quarter past two')"""
    hour = time_obj.hour
    minute = time_obj.minute

    # Convert to 12-hour format
    hour_12 = hour % 12
    if hour_12 == 0:
        hour_12 = 12

    next_hour = (hour_12 % 12) + 1
    period = (
        "in the morning"
        if 5 <= hour < 12
        else "in the afternoon"
        if 12 <= hour < 17
        else "in the evening"
        if 17 <= hour < 21
        else "at night"
    )

    # Format based on minute patterns
    if minute == 0:
        return f"{hour_12} o'clock {period}"
    elif minute == 15:
        return f"quarter past {hour_12} {period}"
    elif minute == 30:
        return f"half past {hour_12} {period}"
    elif minute == 45:
        return f"quarter to {next_hour} {period}"
    elif minute < 30:
        return f"{minute} minutes past {hour_12} {period}"
    else:
        return f"{60 - minute} minutes to {next_hour} {period}"


def parse_time_string(time_str: str) -> Optional[time]:
    """Parse a time string in various formats"""
    formats = [
        "%H:%M",  # 14:30
        "%H:%M:%S",  # 14:30:45
        "%I:%M %p",  # 2:30 PM
        "%I:%M:%S %p",  # 2:30:45 PM
        "%I %p",  # 2 PM
    ]

    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue

    # Try to handle more natural language patterns
    time_patterns = [
        # "3 o'clock" or "3 o clock"
        (
            r"(\d{1,2})\s*(?:o['']?clock|o\s*clock)",
            lambda m: time(
                hour=int(m.group(1)) % 12 + (12 if "pm" in time_str.lower() else 0),
                minute=0,
            ),
        ),
        # "quarter past 3" or "15 past 3"
        (
            r"(?:quarter|(\d{1,2}))\s*past\s*(\d{1,2})",
            lambda m: time(
                hour=int(m.group(2)) % 12 + (12 if "pm" in time_str.lower() else 0),
                minute=15 if m.group(1) is None else int(m.group(1)),
            ),
        ),
        # "quarter to 4" or "15 to 4"
        (
            r"(?:quarter|(\d{1,2}))\s*to\s*(\d{1,2})",
            lambda m: time(
                hour=(int(m.group(2)) - 1) % 12
                + (12 if "pm" in time_str.lower() else 0),
                minute=45 if m.group(1) is None else 60 - int(m.group(1)),
            ),
        ),
        # "half past 3"
        (
            r"half\s*past\s*(\d{1,2})",
            lambda m: time(
                hour=int(m.group(1)) % 12 + (12 if "pm" in time_str.lower() else 0),
                minute=30,
            ),
        ),
    ]

    time_str_lower = time_str.lower()
    for pattern, time_func in time_patterns:
        match = re.search(pattern, time_str_lower)
        if match:
            try:
                return time_func(match)
            except (ValueError, IndexError):
                continue

    return None


def get_time_period(hour: int) -> str:
    """Return the time period description based on hour"""
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


async def get_time(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    """
    Handle time inquiries

    intent: get_time
    """
    # Default to current time
    now = datetime.now()
    target_time = now.time()
    is_specific_time = False
    original_time_str = None

    # Check for time entity
    if "time" in entities and entities["time"]:
        time_entity = entities["time"][0]["value"]

        # Handle specific time
        if "time" in time_entity:
            time_str = time_entity.get("time")
            original_time_str = time_str
            parsed_time = parse_time_string(time_str)

            if parsed_time:
                target_time = parsed_time
                is_specific_time = True

    # Check for raw time in text
    elif "text" in context:
        text = context.get("text", "")

        # Look for HH:MM pattern
        time_matches = re.findall(
            r"\b(\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm)?)\b", text, re.IGNORECASE
        )
        if time_matches:
            original_time_str = time_matches[0]
            parsed_time = parse_time_string(original_time_str)
            if parsed_time:
                target_time = parsed_time
                is_specific_time = True

    # Format time in different ways
    formatted_time = target_time.strftime("%I:%M %p").lstrip("0")  # 2:30 PM
    digital_time = target_time.strftime("%H:%M")  # 14:30
    speech_time = format_time_for_speech(target_time)  # Two thirty PM
    natural_time = format_time_words(target_time)  # half past two in the afternoon

    # Get period of day
    period = get_time_period(target_time.hour)

    # For current time only - add relative descriptions
    is_current_time = not is_specific_time
    hour_now = now.hour
    minute_now = now.minute

    hour_diff = target_time.hour - hour_now
    minute_diff = target_time.minute - minute_now
    total_minute_diff = hour_diff * 60 + minute_diff

    relative_description = ""
    if is_current_time:
        relative_description = "now"
    elif -5 <= total_minute_diff < 0:
        relative_description = f"{abs(total_minute_diff)} minutes ago"
    elif 0 < total_minute_diff <= 5:
        relative_description = f"in {total_minute_diff} minutes"

    return {
        "data": {
            "time": target_time,
            "formatted_time": formatted_time,  # 2:30 PM
            "digital_time": digital_time,  # 14:30
            "speech_time": speech_time,  # two thirty PM
            "natural_time": natural_time,  # half past two in the afternoon
            "hour": target_time.hour,
            "minute": target_time.minute,
            "second": target_time.second,
            "hour_12": target_time.hour % 12 if target_time.hour % 12 != 0 else 12,
            "period": "AM" if target_time.hour < 12 else "PM",
            "time_of_day": period,
            "is_specific_time": is_specific_time,
            "original_time_str": original_time_str,
            "is_current_time": is_current_time,
            "relative_description": relative_description,
            "timezone": "local",
        }
    }
