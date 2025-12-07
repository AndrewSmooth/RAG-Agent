import os
import json
from typing import List, Dict, Any
from langchain_core.documents import Document
import hashlib

from rag.src.utils.clients import get_chroma_client

class KnowledgeBaseLoader:
    def __init__(
        self,
        kb_path: str,
        chroma_url: str,
        yandex_api_key: str,
        yandex_folder_id: str,
    ):
        self.kb_path = kb_path
        self.chroma_url = chroma_url,
        self.yandex_api_key = yandex_api_key,
        self.yandex_folder_id = yandex_folder_id,


    def load_docs(self) -> List[Document]:
        docs_dir = os.path.join(self.kb_path, "docs")
        docs = []
        for filename in os.listdir(docs_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(docs_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                docs.append(
                    Document(
                        page_content=content,
                        metadata={"source": filename, "type": "doc"}
                    )
                )
        return docs

    def load_t2t_docs(self, file: Any = None) -> List[Document]:
        t2t_docs = []

        def append_doc(file_content: Any, file_name: str) -> None:
            t2t_docs.append(
                Document(
                    page_content=file_content,
                    metadata={
                        "source": file_name,
                        "type": "t2t_doc"
                    }
                )
            )
            print(f"✅ Загружен: {filename}")

        if file:
            append_doc(file.read(), file.filename)
        else:
            t2t_docs_dir = os.path.join(self.kb_path, "t2t_docs")

            for filename in os.listdir(t2t_docs_dir):
                filepath = os.path.join(t2t_docs_dir, filename)

                if not (filename.lower().endswith(".txt") or filename.lower().endswith(".md")):
                    continue

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        append_doc(content, filename)

                except Exception as e:
                    print(f"❌ Ошибка чтения {filename}: {e}")
                    continue

        return t2t_docs

    def load_sql_examples(self) -> List[Document]:
        sql_dir = os.path.join(self.kb_path, "sql_examples")
        examples = []
        for filename in os.listdir(sql_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(sql_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                examples.append(
                    Document(
                        page_content=f"Question: {data['question']}\nSQL: {data['sql']}",
                        metadata={
                            "source": filename,
                            "type": "sql_example",
                            "question": data["question"]
                        }
                    )
                )
        return examples

    def load_file(
            self,
            file: Any,
            doc_type: str = None
    ):
        if not doc_type:
            return {'error': 'Не указан тип документа'}

        doc = []

        if doc_type == 't2t_docs':
            doc = self.load_t2t_docs(file=file)
        # elif doc_type == 'docs':
        #     doc = self.load_docs(file=file)
        # elif doc_type == 'sql_examples':
        #     doc = self.load_sql_examples(file=file)

        if not doc:
            return {'error': f'Указан недопустимый тип документа: {doc_type}'}

        chroma_client, embedding_fn = get_chroma_client(
            chroma_url=self.chroma_url,
            yandex_api_key=self.yandex_api_key,
            yandex_folder_id=self.yandex_folder_id
        )

        chroma_collection = chroma_client.get_or_create_collection(
            name=doc_type,
            embedding_function=embedding_fn
        )

        doc_id = f'{doc_type}_{self.hash_filename(file.filename)}'
        existing = chroma_collection.get(ids=[doc_id])

        if existing['ids']:
            print(f"⚠️ Документ с ID '{doc_id}' уже существует. Пропускаем.")
        else:
            chroma_collection.add(
                ids=[doc_id],
                documents=[doc[0]['page_content']],
                metadatas=[doc[0]['metadata']],
            )
            print(f"✅ Добавлен новый документ: {doc_id}")

        return {'ok': True}

    @staticmethod
    def hash_filename(filename: str, length: int = 16) -> str:
        return hashlib.sha256(filename.encode()).hexdigest()[:length]
