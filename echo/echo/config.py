from pathlib import Path

import yaml


class EchoConfig:
    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else Path.cwd()

        # Component paths
        self.entities_path = self.config_path / "entities"
        self.sentences_path = self.config_path / "sentences"
        self.responses_path = self.config_path / "responses"
        self.mappings_path = self.config_path / "mappings"

        # Ensure paths exist
        self._validate_paths()

        # Load configurations
        self.entities = self._load_entities()
        self.intents = self._load_intents()
        self.responses = self._load_responses()

    def _validate_paths(self):
        required_paths = [self.entities_path, self.sentences_path, self.responses_path]

        for path in required_paths:
            if not path.exists():
                raise FileNotFoundError(
                    f"Required configuration directory not found: {path}"
                )

    def _load_yaml_from_dir(self, directory):
        result = {}
        if not directory.exists():
            return result

        for file_path in directory.glob("*.yaml"):
            with open(file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if data:
                    result.update(data)

        return result

    def _load_entities(self):
        all_entity_files = {}
        for file_path in self.entities_path.glob("*.yaml"):
            with open(file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if data and "entities" in data:
                    all_entity_files.update(data["entities"])

        return all_entity_files

    def _load_intents(self):
        all_intents = {}
        for file_path in self.sentences_path.glob("*.yaml"):
            with open(file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if data and "intents" in data:
                    all_intents.update(data["intents"])

        return all_intents

    def _load_responses(self):
        all_responses = {}
        for file_path in self.responses_path.glob("*.yaml"):
            with open(file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if data and "responses" in data and "intents" in data["responses"]:
                    all_responses.update(data["responses"]["intents"])

        return all_responses
