from typing import Dict, Any
import random


def get_weather(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    location = entities.get("location", "your current location")

    conditions = ["sunny", "partly cloudy", "overcast", "rainy", "stormy"]
    temperatures = {
        "sunny": "75°F",
        "partly cloudy": "68°F",
        "overcast": "62°F",
        "rainy": "55°F",
        "stormy": "50°F",
    }

    condition = entities.get("condition", random.choice(conditions))
    temperature = temperatures.get(condition, "70°F")

    return {
        "response": f"The weather in {location} is {condition} with a temperature of {temperature}.",
        "action": None,
        "data": {
            "location": location,
            "condition": condition,
            "temperature": temperature,
        },
    }
