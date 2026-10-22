from curriculum_aligned_ai_assistant.config import Settings
from curriculum_aligned_ai_assistant.graph import AgentGraph, build_graph
from curriculum_aligned_ai_assistant.llm import make_llm
from curriculum_aligned_ai_assistant.retrieval import open_retriever
from curriculum_aligned_ai_assistant.web_search import TavilyWebSearcher


def build_agent(
    collection_name: str, settings: Settings | None = None
) -> tuple[AgentGraph, list[str]]:
    """Build the real agent for one Chroma collection. Returns the graph and startup warnings."""
    settings = settings or Settings.from_env()
    warnings: list[str] = []
    retriever = open_retriever(settings, collection_name)
    llm = make_llm(settings)
    web_searcher: TavilyWebSearcher | None = None
    if settings.tavily_api_key:
        web_searcher = TavilyWebSearcher(settings.tavily_api_key)
    else:
        warnings.append(
            "TAVILY_API_KEY is not set: questions outside the course materials "
            "will not be searched on the web."
        )
    graph = build_graph(
        retriever, web_searcher, llm, k=settings.retrieval_k, max_distance=settings.max_distance
    )
    return graph, warnings
