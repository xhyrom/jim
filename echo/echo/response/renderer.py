import random


class ResponseRenderer:
    def __init__(self, config=None):
        self.config = config

    def render(self, response_key, context, responses=None):
        if responses is None:
            if self.config and hasattr(self.config, "responses"):
                responses = self.config.responses
            else:
                return "Response template not found: no responses available"

        parts = response_key.split(".", 1)
        if len(parts) != 2:
            return f"Invalid response key format: {response_key}"

        intent_name, context_name = parts

        intent_responses = responses.get(intent_name, {})
        if not intent_responses:
            return f"No responses found for intent: {intent_name}"

        if context_name != "default" and "contexts" in intent_responses:
            context_responses = intent_responses.get("contexts", {})
            response_templates = context_responses.get(context_name)

            if not response_templates:
                response_templates = [
                    intent_responses.get(
                        "default", f"No template found for {intent_name}.{context_name}"
                    )
                ]
        else:
            response_templates = [
                intent_responses.get(
                    "default", f"No default template found for {intent_name}"
                )
            ]

        if isinstance(response_templates, list) and response_templates:
            template = random.choice(response_templates)
        else:
            template = response_templates

        try:
            return self._fill_template(template, context)
        except KeyError as e:
            return f"Error: Missing context variable {e} in template"
        except Exception as e:
            return f"Error rendering response: {e}"

    def _fill_template(self, template, context):
        if not isinstance(template, str):
            return str(template)

        safe_context = {}
        for key, value in context.items():
            if value is None:
                safe_context[key] = "(not specified)"
            else:
                safe_context[key] = value

        return template.format(**safe_context)
