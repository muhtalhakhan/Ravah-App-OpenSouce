from fastapi import APIRouter
from app.agent import AgentQuery, AgentResponse, AgentStatus
from app.factory import get_agent

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/query", response_model=AgentResponse)
def query_agent(query: AgentQuery):
    agent = get_agent()
    result = agent.process_query(query.query, query.context)
    return AgentResponse(
        result=result["result"],
        framework=agent.get_framework_name(),
        structured=result.get("structured"),
        metadata=result.get("metadata")
    )


@router.get("/status", response_model=AgentStatus)
def get_agent_status():
    agent = get_agent()
    return AgentStatus(
        framework=agent.get_framework_name(),
        available=agent.is_available(),
        mock_mode=agent.mock_mode
    )
