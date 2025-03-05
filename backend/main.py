from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.websocket import router as websocket_router
from api.routes.approval import router as approval_router
from api.routes.agreement import router as agreement_router
import uvicorn
import os
from contextlib import asynccontextmanager
from database.connection import conn_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn_manager.connect()
    try:
        yield
    finally:
        await conn_manager.disconnect()


app = FastAPI(lifespan=lifespan)


CORS_ALLOWED_ORIGIN = os.getenv("CORS_ALLOWED_ORIGIN", "http://localhost:5173")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(websocket_router)
app.include_router(approval_router)
app.include_router(agreement_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
