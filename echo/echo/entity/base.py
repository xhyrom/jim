import re
from abc import ABC

from ..utils.regex import pattern_complexity


class Entity(ABC):
    def __init__(self, name, config):
        self.name = name
        self.type = config.get("type", name)
        self.description = config.get("description", "")
        self.examples = config.get("examples", [])
        self.patterns = config.get("patterns", [])

        self.pattern_specificity = []
        self.compiled_patterns = []

        for pattern in self.patterns:
            specificity = pattern_complexity(pattern)
            self.pattern_specificity.append(specificity)

            # Compile pattern
            self.compiled_patterns.append(re.compile(pattern, re.IGNORECASE))

    def extract(self, text):
        results = []

        sorted_items = sorted(
            zip(self.compiled_patterns, self.pattern_specificity),
            key=lambda x: x[1],
            reverse=True,
        )

        for pattern, specificity in sorted_items:
            for match in pattern.finditer(text):
                if self.name in match.groupdict():
                    value = match.group(self.name)
                    start, end = match.span(self.name)

                    processed_value = self.process_value(value)

                    results.append(
                        {
                            "entity": self.name,
                            "value": processed_value,
                            "raw_value": value,
                            "start": start,
                            "end": end,
                            "specificity": specificity,
                        }
                    )

        return results

    def process_value(self, raw_value):
        """Process the raw extracted value into a structured format."""

        return raw_value

    def validate_value(self, raw_value):
        for pattern in self.compiled_patterns:
            if pattern.fullmatch(raw_value):
                return 0.7
            elif pattern.search(raw_value):
                return 0.5

        return 0.3
