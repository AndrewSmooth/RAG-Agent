from chromadb import HttpClient

from chromadb.api.types import (
    Documents,
    EmbeddingFunction,
    Embeddings
)

import os

import numpy as np

class YandexEmbeddingFunction:
    def __init__(self, api_key: str, folder_id: str):
        self.api_key = api_key
        self.folder_id = folder_id
        self.url = "https://llm.api.cloud.yandex.net/v1"
        self.doc_model = f"emb://{folder_id}/text-search-doc/latest"
        self.query_model = f"emb://{folder_id}/text-search-query/latest"
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=self.url)

    def __call__(self, input : Documents) -> Embeddings:
        embeddings = []
        for text in input:
            resp = self.client.embeddings.create(
                input=text,
                model=self.doc_model,
                encoding_format="float"
            )
            embedding_array = np.array(resp.data[0].embedding, dtype=np.float32)
            embeddings.append(embedding_array)
        return embeddings
        
    def embed_query(self, input: str):
        """Embed a single query text."""
        output = self([input])
        return output
        
    def embed_documents(self, texts: list):
        """Embed multiple document texts."""
        return self(texts)
    
    def name(self):
        return f"yandex-embeddings-{self.folder_id}"

def get_chroma_client(
    chroma_url: str = "http://localhost:8000",
    yandex_api_key: str = None,
    yandex_folder_id: str = None
):
    print('good')
    client = HttpClient(host="localhost", port=8016)

    embedding_function = YandexEmbeddingFunction(
        api_key=yandex_api_key,
        folder_id=yandex_folder_id
    )

    return client, embedding_function


