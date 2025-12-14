"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from collections.abc import Callable
from typing import Any

from langgraph.runtime import get_runtime
from react_agent.context import Context
from .utils import get_mcp_client

async def call_mcp_tool(tool_name: str, tool_args: dict[str, Any]) -> Any:
    """Вызывает MCP-тул через клиент."""
    # Предполагается, что MCP-клиент уже инициализирован и доступен
    mcp_client = await get_mcp_client()  # ← важно: клиент должен быть в контексте

    result = await mcp_client.call_tool(tool_name, tool_args)
    return result.content  # или result, в зависимости от структуры

async def generate_sql(query: str) -> dict:
    """Генерирует SQL по базе знаний и возвращает его"""

    try:
        result = await call_mcp_tool(
            "generate_sql",
            {
                "query": query,
            },
        )
    except Exception as e:
        results = f"Error calling MCP tool: {str(e)}"

    return {
        "query": query,
        "result": result,
    }


TOOLS: list[Callable[..., Any]] = [generate_sql]
