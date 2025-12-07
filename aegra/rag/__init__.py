import sys
from pathlib import Path

from rag.src.utils.clients import get_chroma_client
from rag.src.utils.kb_loader import kb_loader

config_path = Path(__file__).parent.parent.parent / "config.py"

sys.path.insert(0, str(config_path.parent))

from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

chroma_client, embedding_fn = get_chroma_client(YANDEX_API_KEY, YANDEX_FOLDER_ID)