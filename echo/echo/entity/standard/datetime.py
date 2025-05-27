"""Standard datetime entity implementations."""

import re
from datetime import datetime, timedelta

from ..base import Entity


class DateEntity(Entity):
    def process_value(self, raw_value):
        lower_value = raw_value.lower()
        today = datetime.now().date()

        if lower_value == "today":
            return {"date": today.isoformat(), "type": "relative", "relative": "today"}
        elif lower_value == "tomorrow":
            date = today + timedelta(days=1)
            return {
                "date": date.isoformat(),
                "type": "relative",
                "relative": "tomorrow",
            }
        elif lower_value == "yesterday":
            date = today - timedelta(days=1)
            return {
                "date": date.isoformat(),
                "type": "relative",
                "relative": "yesterday",
            }

        day_pattern = r"(next|last|this)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        day_match = re.match(day_pattern, lower_value, re.IGNORECASE)
        if day_match:
            return {
                "date": lower_value,
                "type": "day_reference",
                "relative": day_match.group(1),
                "day": day_match.group(2),
            }

        date_pattern = r"(\d{1,2})/(\d{1,2})/(\d{2,4})"
        date_match = re.match(date_pattern, lower_value)
        if date_match:
            month = int(date_match.group(1))
            day = int(date_match.group(2))
            year = int(date_match.group(3))

            # Handle 2-digit years
            if year < 100:
                year += 2000

            try:
                date = datetime(year, month, day).date()
                return {
                    "date": date.isoformat(),
                    "type": "specific",
                    "month": month,
                    "day": day,
                    "year": year,
                }
            except ValueError:
                pass

        return {"date": raw_value, "type": "unknown"}


class TimeEntity(Entity):
    def process_value(self, raw_value):
        lower_value = raw_value.lower()

        time_pattern = r"(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?"
        time_match = re.match(time_pattern, lower_value)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            period = time_match.group(3)

            if period:
                period = period.upper()
                if period == "PM" and hour < 12:
                    hour += 12
                elif period == "AM" and hour == 12:
                    hour = 0

            return {
                "time": f"{hour:02d}:{minute:02d}",
                "type": "specific",
                "hour": hour,
                "minute": minute,
            }

        named_times = {
            "morning": {"time": "09:00", "period": "morning"},
            "noon": {"time": "12:00", "period": "noon"},
            "afternoon": {"time": "15:00", "period": "afternoon"},
            "evening": {"time": "19:00", "period": "evening"},
            "night": {"time": "22:00", "period": "night"},
            "midnight": {"time": "00:00", "period": "midnight"},
        }

        if lower_value in named_times:
            return {
                "time": named_times[lower_value]["time"],
                "type": "period",
                "period": named_times[lower_value]["period"],
            }

        return {"time": raw_value, "type": "unknown"}


class DurationEntity(Entity):
    def process_value(self, raw_value):
        lower_value = raw_value.lower()

        duration_pattern = r"(\d+)\s+(second|minute|hour|day|week|month|year)s?"
        duration_match = re.match(duration_pattern, lower_value)
        if duration_match:
            amount = int(duration_match.group(1))
            unit = duration_match.group(2)

            return {
                "duration": raw_value,
                "type": "specific",
                "amount": amount,
                "unit": unit,
            }

        indefinite_pattern = r"(a|an|one)\s+(second|minute|hour|day|week|month|year)"
        indefinite_match = re.match(indefinite_pattern, lower_value)
        if indefinite_match:
            unit = indefinite_match.group(2)

            return {
                "duration": raw_value,
                "type": "indefinite",
                "amount": 1,
                "unit": unit,
            }

        return {"duration": raw_value, "type": "unknown"}
