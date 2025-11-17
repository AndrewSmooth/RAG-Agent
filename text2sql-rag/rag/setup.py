import argparse

from src.utils.kb_loader import load_knowledge_base_to_chroma

parser = argparse.ArgumentParser()
parser.add_argument("--load-kb", action="store_true")
args = parser.parse_args()

if args.load_kb:

    from dotenv import load_dotenv
    import os

    load_dotenv()

    YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
    YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER")
    load_knowledge_base_to_chroma(
        kb_path="knowledge_base",
        chroma_url="http://localhost:8016",
        yandex_api_key=YANDEX_CLOUD_API_KEY,
        yandex_folder_id=YANDEX_CLOUD_FOLDER
    )
else:
    print("no")

