from fastapi import FastAPI
from pydantic import BaseModel
from api.routes.websocket import router as websocket_router
from api.routes.approval import router as approval_router
import uvicorn
from doc_agent import create_agreement_details, AgreementRequest

app = FastAPI()

app.include_router(websocket_router)
app.include_router(approval_router)

@app.post("/create-agreement")
async def create_agreement(request: AgreementRequest):
    return await create_agreement_details(request)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
