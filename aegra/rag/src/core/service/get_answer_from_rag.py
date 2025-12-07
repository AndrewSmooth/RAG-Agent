import os
from dotenv import load_dotenv

from aegra.rag import get_chroma_client
from langchain_openai import ChatOpenAI

from .generate_sql.generate import GenerateSQLService
from .generate_text.generate import GenerateTextService


def generate_answer(query: str, type: str = 't2t') -> str | None:
    """Generates answers from t2t or t2sql"""

    if not query:
        return None

    load_dotenv()

    yandex_api_key = os.getenv("YANDEX_CLOUD_API_KEY")
    yandex_folder_id = os.getenv("YANDEX_CLOUD_FOLDER")

    chroma_client, embedding_fn = get_chroma_client(
        yandex_api_key=yandex_api_key,
        yandex_folder_id=yandex_folder_id
    )

    llm = ChatOpenAI(
        api_key=yandex_api_key,
        base_url="https://llm.api.cloud.yandex.net/v1",
        model=f"gpt://{yandex_folder_id}/yandexgpt-lite",
        temperature=0.1,
        max_tokens=2000,
    )

    if type == "t2t":
        generate_service = GenerateTextService(chroma_client, embedding_fn, llm)
    #TODO: may be work. Needs test
    # elif type == "t2sql":
    #     generate_service = GenerateSQLService(chroma_client, embedding_fn, llm)
    else:
        return None
    return generate_service.generate(query)
