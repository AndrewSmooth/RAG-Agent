from langchain_core.embeddings import Embeddings
import openai
import numpy as np


class YandexCloudEmbeddings(Embeddings):
    def __init__(self, api_key: str, folder_id: str, base_url: str = "https://llm.api.cloud.yandex.net/v1"):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.folder_id = folder_id
        self.doc_model = f"emb://{folder_id}/text-search-doc/latest"
        self.query_model = f"emb://{folder_id}/text-search-query/latest"

    def embed_documents(self, texts):
        """Генерация эмбеддингов для документов"""
        embeddings = []
        for text in texts:
            trimmed = ' '.join(text.split())
            response = self.client.embeddings.create(
                input=trimmed,
                model=self.doc_model,
                encoding_format="float"
            )
            embeddings.append(response.data[0].embedding)
        return embeddings

    def embed_query(self, text):
        """Генерация эмбеддингов для запроса"""
        trimmed = ' '.join(text.split())
        response = self.client.embeddings.create(
            input=trimmed,
            model=self.query_model,
            encoding_format="float"
        )
        return response.data[0].embedding
