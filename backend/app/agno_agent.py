"""
Agno agent implementation.
Note: Agno is a hypothetical/emerging framework. This is a placeholder implementation.
"""

from app.base import BaseAgent


class AgnoAgent(BaseAgent):
    """
    Agent implementation using Agno framework.
    Agno is designed as a lightweight agent framework.
    """

    def __init__(self, mock_mode: bool = True):
        super().__init__(mock_mode)
        self.framework_name = "agno"

    def process_query(self, query: str, context: dict | None = None) -> dict:
        """
        Process query using Agno framework.
        
        In mock mode, returns a simulated response.
        In production mode, would use Agno's agent system.
        """
        if self.mock_mode:
            return self._mock_response(query, context)

        try:
            # Real Agno implementation would look like:
            # from agno import Agent, Task
            #
            # agent = Agent(
            #     name="Assistant",
            #     instructions="You are a helpful AI assistant"
            # )
            #
            # result = agent.run(query)
            #
            # return {
            #     "result": result,
            #     "metadata": {"framework": "agno"}
            # }

            return self._mock_response(query, context)

        except Exception as e:
            return {
                "result": f"Error processing query with Agno: {str(e)}",
                "structured": None,
                "metadata": {"error": True, "framework": "agno"},
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
                "framework": "agno",
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
        """Check if Agno is available."""
        if self.mock_mode:
            return True

        try:
            import agno  # noqa: F401

            return True
        except ImportError:
            return False
