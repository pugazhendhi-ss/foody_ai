import redis
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

class MemoryManager:
    def __init__(self, tenant_id: str, redis_url: str = "redis://localhost:6379/0"):
        self.tenant_id = tenant_id
        self.redis_url = redis_url
        self.redis_client = redis.Redis.from_url(self.redis_url)
        self.memory = self._build_memory()

    def _build_memory(self):
        history = RedisChatMessageHistory(
            session_id=self.tenant_id,
            url=self.redis_url
        )
        return ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=history,
            return_messages=True
        )

    def get_memory(self):
        return self.memory

    def clear_memory(self):
        """Clear the current tenant's chat history."""
        keys = self.redis_client.keys(f"{self.tenant_id}*")
        for key in keys:
            self.redis_client.delete(key)

    def list_sessions(self, pattern="*"):
        """List all session keys matching a pattern (default: all)."""
        return [key.decode("utf-8") for key in self.redis_client.keys(pattern)]

    def delete_session(self, session_key: str):
        """Delete a specific session key manually."""
        return self.redis_client.delete(session_key)
