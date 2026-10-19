from curriculum_aligned_ai_assistant.bootstrap import build_agent
from curriculum_aligned_ai_assistant.graph import AgentGraph


def semantic_graph() -> AgentGraph:
    return build_agent("semantic_chunks")[0]


def hybrid_graph() -> AgentGraph:
    return build_agent("hybrid_chunks")[0]
