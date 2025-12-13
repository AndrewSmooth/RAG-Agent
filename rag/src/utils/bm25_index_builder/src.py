# src/utils/bm25_index_builder.py

import hashlib
import re
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

class BM25IndexBuilder:
    def __init__(self, kb_loader):
        self.kb_loader = kb_loader
        self.corpus = []  # [{"id": str, "text": str, "metadata": dict}]
        self.bm25 = None

    def _generate_id(self, doc_type: str, filename: str) -> str:
        file_hash = hashlib.sha256(filename.encode()).hexdigest()[:16]
        return f"{doc_type}_{file_hash}"

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    def build_index(self) -> 'BM25IndexBuilder':
        """Строим индекс, используя методы kb_loader"""
        self.corpus = []

        # Загружаем все типы документов
        doc_type_map = [
            ("doc", self.kb_loader.load_docs),
            ("sql_example", self.kb_loader.load_sql_examples)
        ]

        for doc_type, load_func in doc_type_map:
            try:
                docs: List[Document] = load_func()
                for doc in docs:
                    source = doc.metadata["source"]
                    doc_id = self._generate_id(doc_type, source)
                    self.corpus.append({
                        "id": doc_id,
                        "text": doc.page_content,
                        "metadata": {
                            "source": source,
                            "type": doc_type,
                            **doc.metadata
                        }
                    })
            except Exception as e:
                print(f"⚠️ Ошибка при загрузке {doc_type}: {e}")

        # Строим BM25
        tokenized_corpus = [self._tokenize(doc["text"]) for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print(f"✅ BM25 индекс построен: {len(self.corpus)} документов")
        return self

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.bm25 is None:
            return []

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = scores.argsort()[::-1][:top_k]

        results = []
        for i in top_indices:
            score = float(scores[i])
            if score > 0:
                doc = self.corpus[i]
                results.append({
                    "id": doc["id"],
                    "text": doc["text"],
                    "score": score,
                    "metadata": doc["metadata"]
                })
        return results
