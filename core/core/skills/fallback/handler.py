import re
from typing import Any, Dict

from ...llm.providers.base import ProviderRegistry
from .prompts import format_fallback_prompt, get_system_prompt


async def llm_fallback(entities: Dict[str, Any], **context) -> Dict[str, Any]:
    """
    Handle queries that couldn't be matched to a specific intent by using an LLM.

    intent: llm_fallback
    """
    config = context.get("config")
    llm_config = config.llm

    if not llm_config.enabled:
        return {
            "data": {
                "response": "I'm not sure I understand. Could you please rephrase your question?",
                "fallback_used": True,
            }
        }

    original_text = context.get("text", "")
    detected_intent = context.get("intent", "unknown")
    confidence = context.get("confidence", 0.0)

    try:
        provider_name = llm_config.provider
        provider_config = llm_config.models.get(provider_name, {})

        llm_provider = ProviderRegistry.get_provider(provider_name, **provider_config)

        system_prompt = get_system_prompt(llm_config.system_prompt)

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": format_fallback_prompt(
                    user_query=original_text,
                    intent_confidence=confidence,
                    detected_intent=detected_intent,
                ),
            },
        ]

        llm_response = await llm_provider.generate_response(
            messages=messages, max_tokens=512, temperature=0.7
        )

        response_text = llm_response.get("content", "")

        response_text = clean_response_for_voice(response_text)

        return {
            "data": {
                "response": response_text,
                "fallback_used": True,
                "original_intent": detected_intent,
                "original_confidence": confidence,
                "provider": llm_response.get("provider"),
                "model": llm_response.get("model"),
            }
        }

    except Exception as e:
        print(f"Error in LLM fallback: {e}")
        return {
            "data": {
                "response": "I'm sorry, but I'm having trouble processing your request right now.",
                "fallback_used": True,
                "error": str(e),
            }
        }


def clean_response_for_voice(text: str) -> str:
    """Clean up an LLM response to make it more suitable for voice output"""

    # Remove markdown formatting
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # Bold
    text = re.sub(r"\*(.*?)\*", r"\1", text)  # Italic
    text = re.sub(r"`(.*?)`", r"\1", text)  # Code
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)  # Code blocks

    # Remove URLs but keep the link text
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)

    # Remove numbered references like [1], [2], etc.
    text = re.sub(r"\[\d+\]", "", text)

    # Remove any remaining markdown symbols
    text = re.sub(r"[#>~]", "", text)

    # Replace multiple newlines with single newlines
    text = re.sub(r"\n{2,}", "\n", text)

    # Replace newlines with spaces for voice output
    text = text.replace("\n", " ")

    # Fix spacing issues
    text = re.sub(r"\s{2,}", " ", text)

    # Trim the response if it's too long (over 300 chars)
    if len(text) > 300:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        result = ""
        for sentence in sentences:
            if len(result) + len(sentence) > 300:
                break
            result += sentence + " "
        text = result.strip()

    return text
