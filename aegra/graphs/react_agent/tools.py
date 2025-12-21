"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from collections.abc import Callable
from typing import Any
import httpx
import uuid

from langgraph.runtime import get_runtime

from react_agent.context import Context


async def search(query: str) -> dict[str, Any] | None:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    runtime = get_runtime(Context)
    return {
        "query": query,
        "max_search_results": runtime.context.max_search_results,
        "results": f"Simulated search results for '{query}'",
    }

# Решил оставить просто чтобы чекать что тулы вообще работают, т.к. не зависит от рага
def calculator(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b


from fastmcp import Client
import asyncio

async def call_mcp_tool(name: str, arguments: dict):
    # Connect via stdio to a local script
    async with Client("../rag/main.py") as client:
        # tools = await client.list_tools()
        # print(f"Available tools: {tools}")
        result = await client.call_tool(name, arguments)
        print(f"Result: {result.content[0].text.strip()}")
        return result.content[0].text.strip()

async def search_knowledge_base(query: str) -> str:
    """Ищи информацию в документации и базе знаний."""
    try:
        result = await call_mcp_tool("search_knowledge_base_tool", {"query": query})
        # T2T-тул в fastmcp обычно возвращает строку в structuredContent
        if isinstance(result, str):
            return result
        else:
            return str(result)
    except Exception as e:
        return f"Ошибка T2T-поиска: {str(e)}"

async def generate_sql_and_run(query: str) -> str:
    """Ответь на вопрос, используя данные из базы."""
    try:
        # Шаг 1: генерация SQL
        print(query)
        gen_result = await call_mcp_tool("generate_sql", {"question": query})
        
        print(gen_result)
        return gen_result

    except Exception as e:
        return f"Ошибка T2SQL: {str(e)}"


TOOLS: list[Callable[..., Any]] = [
    search,
    calculator,
    search_knowledge_base,
    generate_sql_and_run,
]
