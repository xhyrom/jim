import re


def make_optional(pattern):
    """
    Make a pattern optional.

    Args:
        pattern (str): Pattern to make optional

    Returns:
        str: Optional pattern
    """
    return f"(?:{pattern})?"


def make_entity_pattern(entity_name):
    """
    Create a regex pattern for an entity placeholder.

    Args:
        entity_name (str): Entity name

    Returns:
        str: Regex pattern that captures the entity
    """
    return f"(?P<{entity_name}>.*?)"


def is_valid_pattern(pattern):
    """
    Check if a regex pattern is valid.

    Args:
        pattern (str): Pattern to check

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def pattern_complexity(pattern):
    """
    Estimate pattern complexity.

    Args:
        pattern (str): Pattern to analyze

    Returns:
        int: Complexity score (higher is more complex)
    """
    complexity = 0

    special_chars = r"[](){}^$.|*+?\\"
    for char in special_chars:
        complexity += pattern.count(char)

    complexity += len(re.findall(r"\{\w+\}", pattern)) * 2

    return complexity


def convert_entity_placeholders(pattern):
    return re.sub(r"\{(\w+)\}", r"(?P<\1>.*?)", pattern)


def clean_pattern_for_fuzzy(pattern):
    # Remove entity placeholders
    cleaned = re.sub(r"\{\w+\}", "", pattern)

    # Remove common regex patterns
    cleaned = re.sub(r"[\(\)\?\*\+\[\]\{\}\|\\\.\^]", "", cleaned)

    # Remove optional groups (non-capturing)
    cleaned = re.sub(r"\(\?:.*?\)", "", cleaned)

    # Replace multiple spaces with a single space
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned
