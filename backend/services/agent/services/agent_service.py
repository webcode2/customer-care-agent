import os
import re
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from vector_store import vector_store
from prompts import SYSTEM_PROMPT_TEMPLATE

# --- Tool Definitions ---

def internal_retrieve_knowledge(query: str, org_id: str) -> str:
    """
    Core retrieval logic. Searches ChromaDB using strict tenant isolation.
    Rationale: Conversational UIs often prepend "You:" / "Agent:". We strip
    these recursively so the vector search focuses on actual intent.
    """
    clean_query = re.sub(
        r"^((?:You|Agent|Assistant|User):\s*)+", "", query, flags=re.IGNORECASE
    ).strip()
    print(f"\n[RAG] Searching KB for: '{clean_query}' (Org: {org_id})")
    results = vector_store.query(query_texts=[clean_query], tenant_id=str(org_id))
    if results["documents"] and results["documents"][0]:
        formatted_chunks = []
        for i, doc_text in enumerate(results["documents"][0]):
            # metadatas is also a list of lists, matching documents
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            source = meta.get("source", "Unknown Source").split('/')[-1] # Get just the filename
            formatted_chunks.append(f"--- SOURCE: {source} ---\n{doc_text}\n")
        content = "\n".join(formatted_chunks)
    else:
        content = "No information found."
    print(f"[RAG] Retrieved {len(content)} characters of context.")
    return content


@tool
def retrieve_knowledge(query: str, org_id: str):
    """
    Search the business knowledge base for information.
    Use this tool to find answers about the organization, its products, policies, etc.
    """
    return internal_retrieve_knowledge(query, org_id)


# --- State Management ---

class AgentState(TypedDict):
    """
    The State object passed between LangGraph nodes.
    - org_id / user_id : tenant context, never leaves the worker boundary.
    - messages         : full conversation history (auto-merged by LangGraph).
    - turns            : loop-protection counter.
    - max_tokens       : user-defined response length limit.
    """
    org_id: str
    user_id: str
    messages: Annotated[List[BaseMessage], add_messages]
    turns: int
    max_tokens: int


# --- Agent Core Service ---

class AgentService:
    """
    Pure LangGraph ReAct workflow executor.

    Rationale: This class has ONE responsibility — run the LangGraph state
    machine and return the final LLM response string.  Cache lookup/storage
    and NATS transport are handled at higher layers (API controller and
    worker entrypoint respectively), keeping this class simple and testable.
    """

    def __init__(self):
        xai_key = os.getenv("XAI_API_KEY")
        if xai_key:
            self.model = ChatOpenAI(
                model="grok-latest",
                openai_api_key=xai_key,
                openai_api_base="https://api.x.ai/v1",
            ).bind_tools([retrieve_knowledge])
        else:
            self.model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(
                [retrieve_knowledge]
            )

        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", ToolNode([retrieve_knowledge]))
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", self.should_continue)
        workflow.add_edge("tools", "agent")
        self.workflow = workflow.compile()

    def should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        if state.get("turns", 0) >= 5:
            print("MAX TURNS REACHED - FORCING END")
            return END
        if last_message.tool_calls:
            return "tools"
        return END

    def call_model(self, state: AgentState):
        import time
        current_turns = state.get("turns", 0)
        max_tokens = state.get("max_tokens", 500)
        org_id = state["org_id"]
        messages = state["messages"]
        system_msg = SystemMessage(
            content=SYSTEM_PROMPT_TEMPLATE.format(org_id=org_id)
        )

        model_name = getattr(self.model, "model_name", "unknown-model")
        print(
            f"[LLM] ► INITIATED  model={model_name} | org={org_id} "
            f"| turn={current_turns + 1} | max_tokens={max_tokens} "
            f"| prompt_messages={len(messages)}"
        )
        t_start = time.perf_counter()

        try:
            print("reaching out to LLM api")
            response = self.model.invoke(
                [system_msg] + messages, max_tokens=max_tokens
            )
            elapsed = time.perf_counter() - t_start
            tool_calls = getattr(response, "tool_calls", [])
            outcome = f"tool_call={tool_calls[0]['name']}" if tool_calls else "final_answer"
            print(
                f"[LLM] ✓ COMPLETED model={model_name} | org={org_id} "
                f"| turn={current_turns + 1} | latency={elapsed:.2f}s | outcome={outcome}"
            )
        except Exception as exc:
            elapsed = time.perf_counter() - t_start
            print(
                f"[LLM] ✗ FAILED    model={model_name} | org={org_id} "
                f"| turn={current_turns + 1} | latency={elapsed:.2f}s | error={exc}"
            )
            user_query = messages[-1].content
            last_context = internal_retrieve_knowledge(user_query, org_id)
            fallback_msg = AIMessage(
                content=(
                    "⚠️ **LLM API Error**: I couldn't process your request normally, "
                    f"but I retrieved this directly from the knowledge base:\n\n---\n{last_context}"
                )
            )
            return {"messages": [fallback_msg], "turns": current_turns + 1}

        return {"messages": [response], "turns": current_turns + 1}


    async def run(self, org_id: str, user_id: str, query: str, max_tokens: int = 500, history: list = None) -> str:
        """
        Runs the LangGraph workflow and returns the final AI response string.
        No cache logic here — callers own cache lookup/storage.
        """
        if history is None:
            history = []
            
        messages = []
        for msg in history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "agent":
                messages.append(AIMessage(content=msg.get("content", "")))
        
        messages.append(HumanMessage(content=query))

        initial_state = {
            "org_id": org_id,
            "user_id": user_id,
            "messages": messages,
            "turns": 0,
            "max_tokens": max_tokens,
        }
        result = await self.workflow.ainvoke(initial_state)
        return result["messages"][-1].content


# Singleton instance
agent_service = AgentService()
