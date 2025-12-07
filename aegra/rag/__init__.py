from src.utils.clients import get_chroma_client
from src.utils.kb_loader import kb_loader
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

chroma_client, embedding_fn = get_chroma_client(YANDEX_API_KEY, YANDEX_FOLDER_ID)