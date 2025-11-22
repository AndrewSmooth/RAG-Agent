import argparse
import os
from dotenv import load_dotenv

from src.utils.kb_loader import load_knowledge_base_to_chroma
from src.core.service import GenerateService
from src.utils.clients.embedding_client import get_chroma_client
from langchain_openai import ChatOpenAI

def create_app():
    """Create and configure the application."""
    load_dotenv()
    
    # Get environment variables
    yandex_api_key = os.getenv("YANDEX_CLOUD_API_KEY")
    yandex_folder_id = os.getenv("YANDEX_CLOUD_FOLDER")
    
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
    
    # Create GenerateService
    generate_service = GenerateService(chroma_client, embedding_fn, llm)
    
    return generate_service

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load-kb", action="store_true", help="Load knowledge base to Chroma")
    parser.add_argument("--query", type=str, help="Query to convert to SQL")
    args = parser.parse_args()

    if args.load_kb:
        load_knowledge_base_to_chroma(
            kb_path="knowledge_base",
            chroma_url="http://localhost:8016",
            yandex_api_key=os.getenv("YANDEX_CLOUD_API_KEY"),
            yandex_folder_id=os.getenv("YANDEX_CLOUD_FOLDER")
        )
    elif args.query:
        # Create app and process query
        generate_service = create_app()
        result = generate_service.generate(args.query)
        print(f"Generated SQL: {result}")
    else:
        print("Use --load-kb to load knowledge base or --query 'your question' to generate SQL")

if __name__ == "__main__":
    main()

