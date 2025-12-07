from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, CHROMA_DEFAULT_URL, KB_PATH
from .loader import KnowledgeBaseLoader
from .loader_to_chroma import load_knowledge_base_to_chroma


kb_loader = KnowledgeBaseLoader(
    kb_path=KB_PATH,
    chroma_url=CHROMA_DEFAULT_URL,
    yandex_api_key=YANDEX_API_KEY,
    yandex_folder_id=YANDEX_FOLDER_ID
)