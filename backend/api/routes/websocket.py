from fastapi import APIRouter, WebSocket

router = APIRouter()
active_connections = []


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        active_connections.remove(websocket)


async def notify_clients(response: dict):
    """Notify all active WebSocket clients."""
    for connection in active_connections:
        await connection.send_json(response)
