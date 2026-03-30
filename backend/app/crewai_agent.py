"""
CrewAI agent implementation.
"""

from app.base import BaseAgent


class CrewAIAgent(BaseAgent):
    """
    Agent implementation using CrewAI framework.
    CrewAI is designed for multi-agent orchestration and collaboration.
    """

    def __init__(self, mock_mode: bool = True):
        super().__init__(mock_mode)
        self.framework_name = "crewai"

    def process_query(self, query: str, context: dict | None = None) -> dict:
        """
        Process query using CrewAI framework.
        
        In mock mode, returns a simulated response.
        In production mode, would use CrewAI's Agent and Task system.
        """
        if self.mock_mode:
            return self._mock_response(query, context)

        try:
            # Real CrewAI implementation would look like:
            # from crewai import Agent, Task, Crew
            #
            # agent = Agent(
            #     role="Assistant",
            #     goal="Help users with their queries",
            #     backstory="You are a helpful AI assistant",
            #     verbose=True
            # )
            #
            # task = Task(
            #     description=query,
            #     agent=agent
            # )
            #
            # crew = Crew(agents=[agent], tasks=[task])
            # result = crew.kickoff()
            #
            # return {
            #     "result": str(result),
            #     "metadata": {"framework": "crewai", "agents_used": 1}
            # }

            return self._mock_response(query, context)

        except Exception as e:
            return {
                "result": f"Error processing query with CrewAI: {str(e)}",
                "structured": None,
                "metadata": {"error": True, "framework": "crewai"},
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
                "framework": "crewai",
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
        """Check if CrewAI is available."""
        if self.mock_mode:
            return True

        try:
            import crewai  # noqa: F401

            return True
        except ImportError:
            return False
