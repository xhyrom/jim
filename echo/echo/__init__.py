"""
Echo: An intent processing library.
"""

__version__ = "0.0.1"

from .config import EchoConfig
from .entity.extractor import EntityExtractor
from .entity.registry import EntityRegistry
from .intent.matcher import IntentMatcher
from .intent.registry import IntentRegistry
from .response.renderer import ResponseRenderer
from .response.selector import ResponseSelector


class Echo:
    def __init__(self, config_path=None):
        self.config = EchoConfig(config_path)

        # Initialize registries
        self.entity_registry = EntityRegistry(self.config)
        self.intent_registry = IntentRegistry(self.config)

        # Initialize processing components
        self.entity_extractor = EntityExtractor(self.entity_registry)
        self.intent_matcher = IntentMatcher(self.intent_registry)
        self.response_selector = ResponseSelector(self.config)
        self.response_renderer = ResponseRenderer(self.config)

    def process(self, text):
        """
        Process text input to identify intents and extract entities.

        Args:
            text (str): Input text to process

        Returns:
            dict: Processing results with intent, confidence, and entities
        """
        # Match the intent and get the best matching pattern
        intent_results = self.intent_matcher.match(text)

        intent_name = intent_results["intent"]
        confidence = intent_results["confidence"]
        entities = {}

        if intent_name != "fallback" and confidence > 0.5 and "match" in intent_results:
            if "pattern" in intent_results["match"]:
                matched_pattern = intent_results["match"]["pattern"]
                entities = self.entity_extractor.extract_from_pattern(
                    text, matched_pattern
                )

        result = {
            "text": text,
            "intent": intent_name,
            "confidence": confidence,
            "entities": entities,
        }

        return result

    def get_response(self, intent_name, context=None):
        context = context or {}
        response_key = self.response_selector.select(intent_name, context)
        return self.response_renderer.render(response_key, context)


def create_echo(config_path=None):
    return Echo(config_path)
