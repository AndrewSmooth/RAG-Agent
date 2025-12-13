import os
from dotenv import load_dotenv

load_dotenv()

KB_PATH="knowledge_base"
CHROMA_DEFAULT_URL="http://localhost:8016"
YANDEX_API_KEY=os.getenv("YANDEX_CLOUD_API_KEY")
YANDEX_FOLDER_ID=os.getenv("YANDEX_CLOUD_FOLDER")
yandex_api_key=os.getenv("YANDEX_CLOUD_API_KEY")
yandex_folder_id=os.getenv("YANDEX_CLOUD_FOLDER")