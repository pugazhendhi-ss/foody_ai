from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType

from services.tools import add_tool

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


class Assistant:

    def __init__(self):
        self.tools = [add_tool]


    def test_agent(self, instruction):
        test_agent = initialize_agent(
            llm=llm,
            tools=self.tools,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        response = test_agent.invoke(instruction)
        return response


