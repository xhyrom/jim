from . import create_echo

echo = create_echo("../intents/")

result = echo.process("what's the weather like in Seattle tomorrow?")

print(f"Intent: {result['intent']} (Confidence: {result['confidence']:.2f})")
print("Entities:")
for entity_type, entities in result["entities"].items():
    for entity in entities:
        print(f"  - {entity_type}: {entity['raw_value']}")


print(result)

if result["intent"] == "get_weather":
    location = None
    date = None

    if "location" in result["entities"] and result["entities"]["location"]:
        location = result["entities"]["location"][0]["value"]

    if "date" in result["entities"] and result["entities"]["date"]:
        date = result["entities"]["date"][0]["value"]

    weather_context = {
        "location": location or "your location",
        "date": date or "today",
        "weather_condition": "sunny",
        "temperature": "72°F",
        "precipitation": "10% chance of rain",
        "wind": "light breeze",
    }

    print("\nContext:")
    for key, value in weather_context.items():
        print(f"  - {key}: {value}")

    response = echo.get_response(result["intent"], weather_context)

    print(f"\nResponse: {response}")
