from typing import Dict, List, Optional


def format_fallback_prompt(
    user_query: str,
    intent_confidence: float,
    detected_intent: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Format a prompt for the LLM fallback"""

    if not conversation_history:
        conversation_history = []

    prompt = f"""The user said: "{user_query}"

Our intent recognition system detected the intent "{detected_intent}" with a confidence of {intent_confidence:.2f}, which is too low to be reliable.

Please respond to the user's query directly, providing a helpful, concise answer that would work well in a voice conversation. If appropriate, try to identify what the user might be asking for.

Keep your response brief and suitable for voice output.
"""

    return prompt
