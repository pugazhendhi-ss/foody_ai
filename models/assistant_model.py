from pydantic import BaseModel

class ChatPayload(BaseModel):
    user_id: str
    instruction: str


