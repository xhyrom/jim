from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def ask():
    return {"status": "ok", "message": "ask"}
