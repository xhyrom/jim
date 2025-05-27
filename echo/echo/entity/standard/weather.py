import re

from ..base import Entity


class WeatherConditionEntity(Entity):
    def process_value(self, raw_value):
        lower_value = raw_value.lower()

        condition_map = {
            "sunny": "clear",
            "clear": "clear",
            "cloudy": "cloudy",
            "overcast": "cloudy",
            "rainy": "rain",
            "raining": "rain",
            "rain": "rain",
            "showers": "rain",
            "snowy": "snow",
            "snowing": "snow",
            "snow": "snow",
            "stormy": "storm",
            "thunderstorms": "storm",
            "thunderstorm": "storm",
            "windy": "windy",
            "foggy": "fog",
            "misty": "fog",
            "hailing": "hail",
            "hail": "hail",
            "sleeting": "sleet",
            "sleet": "sleet",
        }

        condition = condition_map.get(lower_value)
        if condition:
            return {"condition": condition, "description": raw_value}

        return {"condition": "unknown", "description": raw_value}


class TemperatureEntity(Entity):
    def process_value(self, raw_value):
        lower_value = raw_value.lower()

        temp_pattern = r"(\d+)\s*(?:degrees|°)\s*(C|F|Celsius|Fahrenheit)?"
        temp_match = re.match(temp_pattern, lower_value)
        if temp_match:
            value = int(temp_match.group(1))
            unit = temp_match.group(2)

            if not unit or unit in ("F", "Fahrenheit"):
                unit = "F"
            else:
                unit = "C"

            return {"value": value, "unit": unit, "description": raw_value}

        temp_descriptions = {
            "freezing": {"range": "below_freezing", "estimate": 32, "unit": "F"},
            "cold": {"range": "cold", "estimate": 40, "unit": "F"},
            "cool": {"range": "cool", "estimate": 55, "unit": "F"},
            "mild": {"range": "mild", "estimate": 65, "unit": "F"},
            "warm": {"range": "warm", "estimate": 75, "unit": "F"},
            "hot": {"range": "hot", "estimate": 85, "unit": "F"},
            "boiling": {"range": "very_hot", "estimate": 95, "unit": "F"},
        }

        if lower_value in temp_descriptions:
            return {
                "range": temp_descriptions[lower_value]["range"],
                "estimate": temp_descriptions[lower_value]["estimate"],
                "unit": temp_descriptions[lower_value]["unit"],
                "description": raw_value,
            }

        return {"description": raw_value, "value": None}


class PrecipitationEntity(Entity):
    def process_value(self, raw_value):
        lower_value = raw_value.lower()

        chance_pattern = (
            r"(\d+)%\s+chance of (rain|snow|sleet|hail|showers|thunderstorms)"
        )
        chance_match = re.match(chance_pattern, lower_value)
        if chance_match:
            chance = int(chance_match.group(1))
            type_precip = chance_match.group(2)

            return {
                "type": type_precip,
                "chance": chance,
                "intensity": "unknown",
                "description": raw_value,
            }

        intensity_pattern = (
            r"(light|moderate|heavy)\s+(rain|snow|sleet|hail|showers|drizzle|downpour)"
        )
        intensity_match = re.match(intensity_pattern, lower_value)
        if intensity_match:
            intensity = intensity_match.group(1)
            type_precip = intensity_match.group(2)

            return {
                "type": type_precip,
                "intensity": intensity,
                "chance": 100,
                "description": raw_value,
            }

        return {"description": raw_value}


class WindEntity(Entity):
    def process_value(self, raw_value):
        lower_value = raw_value.lower()

        wind_pattern = r"(\d+)\s+(mph|kmh|knots)\s+(north|south|east|west|northeast|northwest|southeast|southwest)?\s*wind"
        wind_match = re.match(wind_pattern, lower_value)
        if wind_match:
            speed = int(wind_match.group(1))
            unit = wind_match.group(2)
            direction = wind_match.group(3)

            return {
                "speed": speed,
                "unit": unit,
                "direction": direction or "unknown",
                "description": raw_value,
            }

        desc_pattern = r"(light|moderate|strong|high|gale force)\s+(winds?|breeze)"
        desc_match = re.match(desc_pattern, lower_value)
        if desc_match:
            intensity = desc_match.group(1)
            type_wind = desc_match.group(2)

            speed_map = {
                "light": 5,
                "moderate": 15,
                "strong": 25,
                "high": 35,
                "gale force": 45,
            }

            return {
                "intensity": intensity,
                "type": type_wind,
                "speed": speed_map.get(intensity, 0),
                "unit": "mph",
                "description": raw_value,
            }

        return {"description": raw_value}
