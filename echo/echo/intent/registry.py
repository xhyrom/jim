class IntentRegistry:
    def __init__(self, config):
        self.config = config
        self.intents = {}

        # Load intents from configuration
        self._register_intents()

    def _register_intents(self):
        for intent_name, intent_config in self.config.intents.items():
            try:
                self.intents[intent_name] = intent_config
            except Exception as e:
                print(f"Error registering intent {intent_name}: {e}")

    def register_intent(self, intent_name, intent_config):
        self.intents[intent_name] = intent_config

    def get_intent(self, intent_name):
        return self.intents.get(intent_name)

    def get_all_intents(self):
        return self.intents
