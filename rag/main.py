import argparse
import os
import asyncio
import threading
import time

from src.utils.kb_loader import load_knowledge_base_to_chroma, kb_loader
from src.utils.clients.embedding_client import get_chroma_client
import src.core.service.generate_sql.only_semantic as sql_only_semantic
import src.core.service.generate_sql.hybrid as sql_hybrid
import src.core.service.generate_sql.hybrid_with_prompting as sql_hybrid_with_prompting
from src.core.service import GenerateTextService
from src.core.transport.agents.mcp_server import run_mcp_server
from langchain_openai import ChatOpenAI
import psycopg

from config import yandex_api_key, yandex_folder_id

from fastmcp import Client

async def run_mcp_client():
    # Connect via stdio to a local script
    time.sleep(15)
    async with Client("http://0.0.0.0:8008/mcp") as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        result = await client.call_tool("generate_sql", {"query": "Покажи мне всех сотрудников с зарплатой больше 100000"})
        print(f"Result: {result.content[0].text}")

def run_app():
    """Create and configure the application."""
    
    
    # Create chroma client and embedding function
    chroma_client, embedding_fn = get_chroma_client(
        yandex_api_key=yandex_api_key,
        yandex_folder_id=yandex_folder_id
    )

    # Create LLM client
    llm = ChatOpenAI(
        api_key=yandex_api_key,
        base_url="https://llm.api.cloud.yandex.net/v1",
        model=f"gpt://{yandex_folder_id}/yandexgpt-lite",
        temperature=0.1,
        max_tokens=2000,
    )
    # The actual logic is now in setup.py which serves as the main entry point
    # This file can be used for simple demonstrations or testing
    # Create SQL generation service
    generate_sql_service = sql_only_semantic.GenerateSQLService(chroma_client, embedding_fn, llm)
    # generate_sql_service = sql_hybrid_with_prompting.GenerateSQLService(chroma_client, embedding_fn, llm, kb_loader)
    generate_text_service = GenerateTextService(chroma_client, embedding_fn, llm)

    db_params = {
        "host": "localhost",
        "port": 5433,
        "dbname": "postgres",
        "user": "postgres",
        "password": "postgres",
        "autocommit": True
    }
    conn = psycopg.connect(**db_params)
    run_mcp_server(generate_sql_service, generate_text_service, conn)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load-kb", action="store_true", help="Load knowledge base to Chroma")
    args = parser.parse_args()

    if args.load_kb:
        load_knowledge_base_to_chroma(
            kb_path="knowledge_base",
            chroma_url="http://localhost:8016",
            yandex_api_key=os.getenv("YANDEX_CLOUD_API_KEY"),
            yandex_folder_id=os.getenv("YANDEX_CLOUD_FOLDER")
        )
    
    run_app()

if __name__ == "__main__":
    main()

