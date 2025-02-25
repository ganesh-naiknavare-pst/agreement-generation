from fastapi import FastAPI
from api.routes.websocket import router as websocket_router
from api.routes.approval import router as approval_router
import uvicorn

app = FastAPI()

app.include_router(websocket_router)
app.include_router(approval_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
