from chromadb import HttpClient
from chromadb.utils import embedding_functions

import os

class YandexEmbeddingFunction:
    def __init__(self, api_key: str, folder_id: str):
        self.api_key = api_key
        self.folder_id = folder_id
        self.url = "https://llm.api.cloud.yandex.net/v1"
        self.doc_model = f"emb://{folder_id}/text-search-doc/latest"
        self.query_model = f"emb://{folder_id}/text-search-query/latest"
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=self.url)

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        embeddings = []
        for text in input:
            if isinstance(text, str):
                trimmed = ' '.join(text.split())
            else:
                trimmed = str(text)
            model = self.query_model if len(input) == 1 else self.doc_model
            try:
                resp = self.client.embeddings.create(
                    input=trimmed,
                    model=model,
                    encoding_format="float"
                )
                # Get the embedding and ensure it's a list
                embedding = resp.data[0].embedding
                if isinstance(embedding, (list, tuple)):
                    embedding_list = list(embedding)
                elif hasattr(embedding, 'tolist'):
                    embedding_list = embedding.tolist()
                else:
                    embedding_list = [float(embedding)]
                embeddings.append(embedding_list)
            except Exception as e:
                print(f"Error embedding text: {str(text)[:50]}... -> {e}")
                raise
        return embeddings
        
    def embed_query(self, input: str):
        """Embed a single query text."""
        return self([input])[0]
        
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
    client = HttpClient(host="localhost", port=8016)

    embedding_function = YandexEmbeddingFunction(
        api_key=yandex_api_key,
        folder_id=yandex_folder_id
    )

    return client, embedding_function


