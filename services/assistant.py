# Load environment variables first
from dotenv import load_dotenv

from models.assistant_model import ChatPayload

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from services.memory_manager import MemoryManager
from services.tools import search_restaurant_tool, reserve_table_tool
from services.langsmith_manager import TracingManager


# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.02)

class Assistant:
    """Foody-AI Assistant with reservation workflow"""

    def __init__(self, project_name: str = "foody-ai"):
        self.tracing_manager = TracingManager(project_name)

        self.tools = [search_restaurant_tool, reserve_table_tool]
        self.prompt = hub.pull("hwchase17/openai-functions-agent")
        # Create agent
        self.agent = create_openai_functions_agent(llm=llm, tools=self.tools, prompt=self.prompt)


    def chat(self, chat_data: ChatPayload) -> dict:
        """
        Chat interface for the assistant.

        Args:
            chat_data.user_id: Session identifier
            chat_data.query: (e.g., "Find a Chinese restaurant in Mumbai tomorrow at 9 PM")

        Returns:
            Agent's response
        """
        try:
            config = self.tracing_manager.get_config(chat_data.id)
            memory = MemoryManager(chat_data.id).get_memory()

            agent_executor = AgentExecutor(agent=self.agent,
                                           tools=self.tools,
                                           memory = memory,
                                           verbose=True,
                                           handle_parsing_errors=True,
                                           max_iterations=5)

            # Invoke the agent with user input and LangSmith trace config
            response = agent_executor.invoke({"input": chat_data.query}, config=config)
            return {"response": response["output"]}

        except Exception as e:
            return {"response": f"Sorry, I encountered an error: {str(e)}"}


