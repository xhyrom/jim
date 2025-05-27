import re
import string


def normalize_text(text):
    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"\s+", " ", text).strip()

    punctuation_to_remove = (
        string.punctuation.replace("'", "").replace("-", "").replace(".", "")
    )
    text = "".join([c for c in text if c not in punctuation_to_remove])

    return text


def extract_entity_placeholder(pattern):
    """
    Extract entity placeholders from a pattern.

    Args:
        pattern (str): Pattern string

    Returns:
        list: List of entity names
    """
    return re.findall(r"\{(\w+)\}", pattern)
