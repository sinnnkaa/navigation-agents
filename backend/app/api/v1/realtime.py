from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/dialog")
async def dialog_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.close(code=1013, reason="Агент-помощник ещё не реализован")


@router.websocket("/signaling")
async def signaling_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.close(code=1013, reason="WebRTC-сигналинг ещё не реализован")
