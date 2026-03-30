"""
Agent factory for creating agent instances based on configuration.
"""

from app.agno_agent import AgnoAgent
from app.base import BaseAgent
from app.crewai_agent import CrewAIAgent
from app.langchain_agent import LangChainAgent
from app.config import settings


def get_agent() -> BaseAgent:
    """
    Factory function to get the appropriate agent based on AGENT_FRAMEWORK setting.
    
    Falls back to available frameworks in order: CrewAI -> Agno -> LangChain
    
    Returns:
        BaseAgent instance
        
    Raises:
        RuntimeError: If no agent framework is available
    """
    framework = settings.AGENT_FRAMEWORK.lower()
    mock_mode = settings.AGENT_MOCK_MODE

    # Try to use the configured framework
    if framework == "crewai":
        agent = CrewAIAgent(mock_mode=mock_mode)
        if agent.is_available():
            return agent

    elif framework == "agno":
        agent = AgnoAgent(mock_mode=mock_mode)
        if agent.is_available():
            return agent

    elif framework == "langchain":
        agent = LangChainAgent(mock_mode=mock_mode)
        if agent.is_available():
            return agent

    # Fallback logic: try frameworks in order
    for AgentClass in [CrewAIAgent, AgnoAgent, LangChainAgent]:
        agent = AgentClass(mock_mode=mock_mode)
        if agent.is_available():
            return agent

    # If no framework is available, raise error
    raise RuntimeError(
        "No agent framework is available. Please install one of: crewai, agno, langchain"
    )
