from typing import Any

from tavily import TavilyClient

from curriculum_aligned_ai_assistant.state import WebResult


class TavilyWebSearcher:
    def __init__(self, api_key: str, max_results: int = 3, client: Any | None = None) -> None:
        self._max_results = max_results
        self._client = client if client is not None else TavilyClient(api_key=api_key)

    def search(self, question: str) -> list[WebResult]:
        response = self._client.search(query=question, max_results=self._max_results)
        return [
            WebResult(
                title=str(item.get("title", "")),
                url=str(item["url"]),
                content=str(item["content"]),
            )
            for item in response.get("results", [])
            if item.get("url") and item.get("content")
        ]
