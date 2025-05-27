from typing import Any, Dict

from fastapi import APIRouter, Body, Request

router = APIRouter()


@router.post("")
async def ask(request: Request, data: Dict[str, Any] = Body(...)):
    text = data.get("text", "")
    lang = data.get("lang", "en")
    user_id = data.get("user_id", "default")
    device_id = data.get("device_id", "unknown")

    intent_processor = request.app.state.intent_processor

    result = intent_processor.process(text, lang, user_id, device_id)

    return {
        "status": "ok",
        "intent": result.get("intent"),
        "confidence": result.get("confidence"),
        "response": result.get("response"),
        "action": result.get("action", None),
    }
