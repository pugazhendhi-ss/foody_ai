from pydantic import BaseModel

class ChatPayload(BaseModel):
    user_id: str
    query: str


