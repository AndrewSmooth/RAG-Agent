import argparse
import os
from dotenv import load_dotenv

from src.utils.kb_loader import load_knowledge_base_to_chroma
from src.core.service.generate_sql.generate import GenerateSQLService
from src.core.service.generate_text.generate import GenerateTextService
from src.utils.clients.embedding_client import get_chroma_client
from langchain_openai import ChatOpenAI

from config import yandex_api_key, yandex_folder_id

def run_app(query: str = None):
    """Create and configure the application."""
    
    load_dotenv()
    
    # Get environment variables
    
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
    generate_sql_service = GenerateSQLService(chroma_client, embedding_fn, llm)
    user_question = "Show all employees in the Engineering department"
    generated_sql = generate_sql_service.generate(user_question)
    print(f"Question: {user_question}")
    print(f"Generated SQL: {generated_sql}")
    
    # Create text generation service
    generate_text_service = GenerateTextService(chroma_client, embedding_fn, llm)
    if query:
        text_question = query
    else:
        text_question = "What is the employee management system about?"
    generated_text = generate_text_service.generate(text_question)
    print(f"\nQuestion: {text_question}")
    print(f"Generated Text: {generated_text}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load-kb", action="store_true", help="Load knowledge base to Chroma")
    parser.add_argument("--query", type=str, help="Query to convert to SQL")
    args = parser.parse_args()
    query = ''

    if args.load_kb:
        load_knowledge_base_to_chroma(
            kb_path="knowledge_base",
            chroma_url="http://localhost:8016",
            yandex_api_key=os.getenv("YANDEX_CLOUD_API_KEY"),
            yandex_folder_id=os.getenv("YANDEX_CLOUD_FOLDER")
        )
        query = args.query
    
    run_app(query)

if __name__ == "__main__":
    main()

