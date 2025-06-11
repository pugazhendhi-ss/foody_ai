from fastapi import APIRouter, Depends
from models.assistant_model import ChatPayload

from services.assistant import Assistant

assistant_router = APIRouter(tags=["Assistant"])

def get_assistant():
    return Assistant()

@assistant_router.post("/assistant")
def assistant(
        chat_payload: ChatPayload,
        assistant_service: Assistant = Depends(get_assistant)
):
    return assistant_service.chat(chat_payload)



