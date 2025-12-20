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

MCP_URL = "http://localhost:8008/mcp" # 8000 занят аегрой

from fastmcp import Client
import asyncio

async def call_mcp_tool(name: str, arguments: dict):
    # Connect via stdio to a local script
    async with Client("http://0.0.0.0:8008/mcp") as client:
        # tools = await client.list_tools()
        # print(f"Available tools: {tools}")
        result = await client.call_tool(name, arguments)
        print(f"Result: {result.content[0].text.strip()}")
        return result


# def call_mcp_tool1(name: str, arguments: dict) -> dict:
#     payload = {
#         "jsonrpc": "2.0",
#         "id": str(uuid.uuid4()),
#         "method": "tools/call",
#         "params": {
#             "name": "search_knowledge_base_tool",
#             "arguments": arguments
#         }
#     }
#     response = httpx.post(MCP_URL, json=payload, headers={
#             "Accept": "application/json"
#         }, timeout=30)
#     response.raise_for_status()
#     result = response.json()

#     if "error" in result:
#         raise RuntimeError(f"MCP error: {result['error']}")

#     # fastmcp возвращает не просто result, а объект с structuredContent
#     mcp_response = result["result"]
#     return mcp_response["structuredContent"]  # ← вот тут нужные данные

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
        gen_result = await call_mcp_tool("generate_sql", {"query": query})
        print(gen_result.data)
        # fastmcp возвращает строку SQL в structuredContent
        sql = gen_result if isinstance(gen_result, str) else str(gen_result)
        sql = sql.strip()
        print(type(sql), sql)

        if not sql or sql.startswith("-- ОШИБКА"):
            return sql
        
        return {
            "result": sql,
        }

    except Exception as e:
        return f"Ошибка T2SQL: {str(e)}"

TOOLS: list[Callable[..., Any]] = [
    search,
    calculator,
    search_knowledge_base,
    generate_sql_and_run,
]
