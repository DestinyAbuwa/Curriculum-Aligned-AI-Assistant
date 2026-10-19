from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from curriculum_aligned_ai_assistant.nodes import Nodes, route_after_grade
from curriculum_aligned_ai_assistant.ports import Llm, Retriever, WebSearcher
from curriculum_aligned_ai_assistant.state import AgentState

AgentGraph = CompiledStateGraph[AgentState, None, AgentState, AgentState]


def build_graph(
    retriever: Retriever,
    web_searcher: WebSearcher | None,
    llm: Llm,
    k: int,
    max_distance: float,
) -> AgentGraph:
    nodes = Nodes(retriever, web_searcher, llm, k=k, max_distance=max_distance)
    builder = StateGraph(AgentState)
    builder.add_node("retrieve", nodes.retrieve)
    builder.add_node("grade", nodes.grade)
    builder.add_node("web_search", nodes.web_search)
    builder.add_node("generate", nodes.generate)
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "grade")
    builder.add_conditional_edges("grade", route_after_grade, ["generate", "web_search"])
    builder.add_edge("web_search", "generate")
    builder.add_edge("generate", END)
    return builder.compile()
