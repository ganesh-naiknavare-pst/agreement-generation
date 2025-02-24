from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse

app = FastAPI()
active_connections = []
approved_users = set()
rejected_users = set()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        active_connections.remove(websocket)


@app.get("/sign/{user}/approve")
async def approve_user(user: str):
    approved_users.add(user)
    response = {"status": "approved", "user_id": user, "approved": True}
    await notify_clients(response)
    return JSONResponse(content=response)


@app.get("/sign/{user}/reject")
async def reject_user(user: str):
    rejected_users.add(user)
    response = {"status": "rejected", "user_id": user, "approved": False}
    await notify_clients(response)
    return JSONResponse(content=response)


async def notify_clients(response: dict):
    # Notify all WebSocket clients

    for connection in active_connections:
        await connection.send_json(response)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
