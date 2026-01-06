"""
Web search tool for answering questions the agent doesn't know.
"""
import httpx
from typing import Dict, Any
from .base import BaseTool
from ..config import settings
from ..utils.logger import logger


class WebSearchTool(BaseTool):
    """
    Web search tool using Serper API to search Google.
    Falls back to DuckDuckGo if Serper API key is not configured.
    """

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for current information when you don't know the answer "
            "to a customer's question. Use this tool to find up-to-date information, "
            "facts, news, or any knowledge you're uncertain about."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific and clear."
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of search results to return (1-10)",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }

    async def execute(self, query: str, num_results: int = 3) -> Dict[str, Any]:
        """
        Execute web search using Serper API or DuckDuckGo.

        Args:
            query: Search query string
            num_results: Number of results to return (1-10)

        Returns:
            Dictionary with search results or error message
        """
        logger.info(f"Executing web search: query='{query}', num_results={num_results}")

        # Try Serper API first if configured
        if settings.serper_api_key:
            try:
                return await self._search_with_serper(query, num_results)
            except Exception as e:
                logger.warning(f"Serper API search failed: {e}. Falling back to DuckDuckGo.")

        # Fallback to DuckDuckGo
        try:
            return await self._search_with_duckduckgo(query, num_results)
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {
                "success": False,
                "error": "Unable to perform web search at this time",
                "query": query
            }

    async def _search_with_serper(self, query: str, num_results: int) -> Dict[str, Any]:
        """
        Search using Serper API (Google Search).

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            Search results dictionary
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": settings.serper_api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": query,
                    "num": num_results
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            # Parse results
            results = []
            if "organic" in data:
                for item in data["organic"][:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", "")
                    })

            # Add answer box if available
            answer_box = None
            if "answerBox" in data:
                answer_box = data["answerBox"].get("answer") or data["answerBox"].get("snippet")

            return {
                "success": True,
                "query": query,
                "answer_box": answer_box,
                "results": results,
                "source": "Google via Serper"
            }

    async def _search_with_duckduckgo(self, query: str, num_results: int) -> Dict[str, Any]:
        """
        Search using DuckDuckGo Instant Answer API (free, no API key required).

        Args:
            query: Search query
            num_results: Number of results (limited for free API)

        Returns:
            Search results dictionary
        """
        async with httpx.AsyncClient() as client:
            # DuckDuckGo Instant Answer API
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                    "skip_disambig": 1
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            # Parse instant answer
            answer = data.get("AbstractText") or data.get("Answer")

            # Parse related topics as results
            results = []
            related_topics = data.get("RelatedTopics", [])[:num_results]

            for topic in related_topics:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else topic.get("Text", ""),
                        "snippet": topic.get("Text", ""),
                        "link": topic.get("FirstURL", "")
                    })

            return {
                "success": True,
                "query": query,
                "answer_box": answer if answer else None,
                "results": results,
                "source": "DuckDuckGo",
                "note": "For better results, configure SERPER_API_KEY in .env"
            }
