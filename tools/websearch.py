import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

client = TavilyClient(api_key=TAVILY_API_KEY)


def web_search(query: str):
    """Search the web using Tavily."""

    try:
        response = client.search(
    query=query,
    search_depth="advanced",
    max_results=5,
    include_answer=True,
    topic="general",
)

        return response

    except Exception as error:
        return {
            "success": False,
            "message": f"Web search failed: {error}",
        }