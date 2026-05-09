import pytest
from unittest.mock import MagicMock, patch
from ..services.agent_service import AgentService

@pytest.mark.asyncio
async def test_agent_workflow_kb_retriever():
    state = {
        "org_id": "1",
        "user_query": "hello",
        "context": "",
        "response": "",
        "history": []
    }
    
    with patch("backend.services.agent.services.agent_service.vector_store") as mock_vs:
        mock_vs.query.return_value = {"documents": [["doc1", "doc2"]]}
        
        result = AgentService.kb_retriever(state)
        
        assert "doc1" in result["context"]
        assert "doc2" in result["context"]
        mock_vs.query.assert_called_once_with(query_texts=["hello"], tenant_id="1")

@pytest.mark.asyncio
async def test_agent_workflow_responder():
    state = {
        "org_id": "1",
        "user_query": "hello",
        "context": "some info",
        "response": "",
        "history": []
    }
    
    with patch("backend.services.agent.services.agent_service.ChatOpenAI") as mock_llm_class:
        mock_llm = mock_llm_class.return_value
        mock_llm.invoke.return_value = MagicMock(content="AI response")
        
        result = AgentService.responder(state)
        
        assert result["response"] == "AI response"
        mock_llm.invoke.assert_called_once()
        
        # Verify the prompt template was used (indirectly by checking invoke arguments if needed)
