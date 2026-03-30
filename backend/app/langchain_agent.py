"""
LangChain agent implementation.
"""

from app.base import BaseAgent


class LangChainAgent(BaseAgent):
    """
    Agent implementation using LangChain framework.
    LangChain provides comprehensive tools for building LLM applications.
    """

    def __init__(self, mock_mode: bool = True):
        super().__init__(mock_mode)
        self.framework_name = "langchain"

    def process_query(self, query: str, context: dict | None = None) -> dict:
        """
        Process query using LangChain framework.
        
        In mock mode, returns a simulated response.
        In production mode, would use LangChain's agent system.
        """
        if self.mock_mode:
            return self._mock_response(query, context)

        try:
            # Real LangChain implementation would look like:
            # from langchain.agents import AgentExecutor, create_openai_functions_agent
            # from langchain.prompts import ChatPromptTemplate
            # from langchain_openai import ChatOpenAI
            # from langchain.tools import Tool
            #
            # llm = ChatOpenAI(temperature=0)
            #
            # tools = [
            #     Tool(
            #         name="Calculator",
            #         func=lambda x: eval(x),
            #         description="Useful for math calculations"
            #     )
            # ]
            #
            # prompt = ChatPromptTemplate.from_messages([
            #     ("system", "You are a helpful assistant"),
            #     ("human", "{input}"),
            #     ("placeholder", "{agent_scratchpad}"),
            # ])
            #
            # agent = create_openai_functions_agent(llm, tools, prompt)
            # agent_executor = AgentExecutor(agent=agent, tools=tools)
            #
            # result = agent_executor.invoke({"input": query})
            #
            # return {
            #     "result": result["output"],
            #     "metadata": {"framework": "langchain", "tools_used": len(tools)}
            # }

            return self._mock_response(query, context)

        except Exception as e:
            return {
                "result": f"Error processing query with LangChain: {str(e)}",
                "structured": None,
                "metadata": {"error": True, "framework": "langchain"},
            }

    def _mock_response(self, query: str, context: dict | None = None) -> dict:
        """Generate a deterministic founder-focused mock response."""
        prompt = self.build_prompt(query, context)
        structured = self.build_structured_payload(query, context)
        result = self.summarize_structured_payload(structured)
        return {
            "result": result,
            "structured": structured.model_dump(),
            "metadata": {
                "framework": "langchain",
                "mock": True,
                "query_length": len(query),
                "context_provided": context is not None,
                "prompt": prompt,
                "response_type": "founder_content_plan_v1",
            },
        }

    def get_framework_name(self) -> str:
        return self.framework_name

    def is_available(self) -> bool:
        """Check if LangChain is available."""
        if self.mock_mode:
            return True

        try:
            import langchain  # noqa: F401

            return True
        except ImportError:
            return False
