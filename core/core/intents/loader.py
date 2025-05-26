import yaml
import re
from pathlib import Path
from typing import Dict, List, Any
import importlib


class IntentLoader:
    intents_dir: Path
    skills_module: str

    intents: Dict[str, Any]
    handlers: Dict[str, Any]
    compiled_patterns: Dict[str, List[re.Pattern]]

    def __init__(self, intents_dir: Path, skills_module: str = "core.skills"):
        self.intents_dir = intents_dir
        self.skills_module = skills_module

        self.intents = {}
        self.handlers = {}
        self.compiled_patterns = {}

    def load_all_intents(self) -> Dict[str, Any]:
        for yaml_file in self.intents_dir.glob("*.yaml"):
            self.__load_intent_file(yaml_file)

        return self.intents

    def __load_intent_file(self, file_path: Path):
        try:
            with open(file_path, "r") as f:
                config = yaml.safe_load(f)

            skill_name = config.get("skill")
            if not skill_name:
                print(f"Warning: Skill name not specified in {file_path}")
                return

            for intent_config in config.get("intents", []):
                intent_name = intent_config.get("name")
                if not intent_name:
                    print(f"Warning: Intent without name in {file_path}")
                    continue

                self.intents[intent_name] = intent_config

                patterns = intent_config.get("patterns", [])
                self.compiled_patterns[intent_name] = [
                    re.compile(pattern, re.IGNORECASE) for pattern in patterns
                ]

                handler_path = intent_config.get("handler")
                if handler_path:
                    self.__load_handler(intent_name, handler_path)

        except Exception as e:
            print(f"Error loading intent file {file_path}: {e}")

    def __load_handler(self, intent_name: str, handler_path: str):
        try:
            parts = handler_path.split(".")
            if len(parts) < 2:
                print(f"Warning: Invalid handler path {handler_path}")
                return

            module_name = f"{self.skills_module}.{parts[0]}"
            function_name = parts[1]

            module = importlib.import_module(module_name)
            handler_func = getattr(module, function_name)

            self.handlers[intent_name] = handler_func

        except (ImportError, AttributeError) as e:
            print(f"Error loading handler {handler_path}: {e}")
