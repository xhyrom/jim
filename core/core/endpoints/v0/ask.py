from typing import Any, Dict

from fastapi import APIRouter, Body, Request

router = APIRouter()


@router.post("")
async def ask(request: Request, data: Dict[str, Any] = Body(...)):
    text = data.get("text", "")
    lang = data.get("lang", "en")
    user_id = data.get("user_id", "default")
    device_id = data.get("device_id", "unknown")

    echo = request.app.state.echo
    handler_registry = request.app.state.handler_registry
    config = request.app.state.config

    result = echo.process(text)

    result["echo"] = echo

    response_data = handler_registry.process_intent(
        result=result, user_id=user_id, device_id=device_id, config=config
    )

    return {
        "status": "ok",
        "intent": response_data.get("intent"),
        "confidence": response_data.get("confidence"),
        "response": response_data.get("response"),
        "action": response_data.get("action", None),
    }
