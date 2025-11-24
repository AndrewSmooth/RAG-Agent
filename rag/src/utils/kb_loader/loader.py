import os
import json
from typing import List, Dict
from langchain_core.documents import Document

class KnowledgeBaseLoader:
    def __init__(self, kb_path: str):
        self.kb_path = kb_path

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

    def load_t2t_docs(self) -> List[Document]:
        t2t_docs_dir = os.path.join(self.kb_path, "t2t_docs")
        t2t_docs = []
        for filename in os.listdir(t2t_docs_dir):
            filepath = os.path.join(t2t_docs_dir, filename)

            if not (filename.lower().endswith(".txt") or filename.lower().endswith(".md")):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                t2t_docs.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": filename,
                            "type": "t2t_doc"
                        }
                    )
                )
                print(f"✅ Загружен: {filename}")

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
