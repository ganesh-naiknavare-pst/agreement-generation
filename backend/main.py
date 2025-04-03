from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.websocket import router as websocket_router
from api.routes.approval import router as approval_router
from api.routes.agreement import router as agreement_router
from api.routes.user import router as user_router
from api.routes.validation import router as image_validation_router
from api.routes.contact_us import router as contact_router
import uvicorn
import os
from contextlib import asynccontextmanager
from database.connection import conn_manager
from helpers.thread_executer import thread_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn_manager.connect()
    try:
        yield
    finally:
        await conn_manager.disconnect()
        thread_pool.shutdown(wait=True)


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
app.include_router(user_router)
app.include_router(image_validation_router)
app.include_router(contact_router)

# Hello World Endpoint
@app.get("/hello")
async def hello_world():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="192.168.1.76",
        port=8000,
        reload=True,
        ssl_keyfile="192.168.1.76+2-key.pem",
        ssl_certfile="192.168.1.76+2.pem" 
    )
