import os
import json
from typing import List, Dict
from langchain.schema import Document

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
