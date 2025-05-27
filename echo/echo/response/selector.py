import importlib.util
import sys


class ResponseSelector:
    def __init__(self, config):
        self.config = config
        self.mapping_modules = self._load_mapping_modules()

    def select(self, intent_name, context=None):
        context = context or {}

        if intent_name in self.mapping_modules:
            mapping_func = self.mapping_modules[intent_name]
            response_key = mapping_func(context)
        else:
            response_key = f"{intent_name}.default"

        return response_key

    def _load_mapping_modules(self):
        mapping_functions = {}

        mappings_dir = self.config.mappings_path
        if not mappings_dir.exists():
            return mapping_functions

        init_path = mappings_dir / "__init__.py"
        if init_path.exists():
            module_name = f"custom_mappings_{id(self)}"

            spec = importlib.util.spec_from_file_location(module_name, str(init_path))
            mappings_module = importlib.util.module_from_spec(spec)

            sys.modules[module_name] = mappings_module

            spec.loader.exec_module(mappings_module)

            if hasattr(mappings_module, "INTENT_MAPPINGS"):
                mapping_functions = mappings_module.INTENT_MAPPINGS

        return mapping_functions
