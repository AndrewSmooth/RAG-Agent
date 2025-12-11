from chromadb import HttpClient

from chromadb.api.types import (
    Documents,
    EmbeddingFunction,
    Embeddings
)

import requests
import time
import numpy as np

class YandexEmbeddingFunction:
    def __init__(self, api_key: str, folder_id: str):
        self.doc_uri = f"emb://{folder_id}/text-search-doc/latest"
        self.query_uri = f"emb://{folder_id}/text-search-query/latest"
        self.embed_url = "https://llm.api.cloud.yandex.net:443/foundationModels/v1/textEmbedding"
        self.headers = {"Content-Type": "application/json", "Authorization": f"Api-Key {api_key}", "x-folder-id": f"{folder_id}"}
        self.query_model = f"emb://{folder_id}/text-search-query/latest"

    def _embed_text(self, text: str):
        query_data = {
            "modelUri": self.query_uri,
            "text": text,
        }

        response = requests.post(self.embed_url, json=query_data, headers=self.headers)
        response.raise_for_status()
        embedding_list = response.json()["embedding"]
        embedding = np.array(embedding_list, dtype=np.float32)

        # Задержка для соблюдения рейт-лимита (Yandex: ~10 RPS)
        time.sleep(0.1)

        return embedding
    
    def __call__(self, input) -> Embeddings:
        if isinstance(input, list):
            
            return [self._embed_text(text) for text in input]
        elif isinstance(input, str):
            return self._embed_text(input)
        else:
            raise ValueError("wrong type for call embedding function")
        
        
    def embed_query(self, input: str):
        """Embed a single query text."""
        output = self(input)
        return output
        
    def embed_documents(self, texts: list):
        """Embed multiple document texts."""
        pass
    
    def name(self):
        return f"yandex-embeddings-"

def get_chroma_client(
    chroma_url: str = "http://localhost:8000",
    yandex_api_key: str = None,
    yandex_folder_id: str = None
):
    client = HttpClient(host="localhost", port=8016)

    embedding_function = YandexEmbeddingFunction(
        api_key=yandex_api_key,
        folder_id=yandex_folder_id
    )

    return client, embedding_function


