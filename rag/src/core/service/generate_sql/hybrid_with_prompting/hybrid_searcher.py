from typing import List, Dict, Any
from src.utils.semantic_searcher.generate_sql import search_in_knowledge_base
from src.utils.bm25_index_builder import BM25IndexBuilder
import numpy as np

def reciprocal_rank_fusion(results_list: List[List[Dict]], k: int = 60) -> List[Dict]:
    all_ids = {doc["id"] for results in results_list for doc in results}
    rrf_scores = {}
    for results in results_list:
        for rank, doc in enumerate(results):
            doc_id = doc["id"]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (k + rank + 1)
    return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

def hybrid_search(
    query: str,
    chroma_client,
    embedding_fn,
    bm25_index_builder: BM25IndexBuilder,
    top_k: int = 5
) -> Dict[str, Any]:
    # 1. Семантический поиск
    sem_results = search_in_knowledge_base(query, chroma_client, embedding_fn)
    semantic_docs = [
        {"id": doc_id, "score": 1 / (1 + dist)}
        for doc_id, dist in zip(sem_results["ids"], sem_results["distances"])
    ]

    # 2. BM25 поиск
    bm25_docs = bm25_index_builder.search(query, top_k=top_k)
    bm25_results = [{"id": doc["id"], "score": doc["score"]} for doc in bm25_docs]

    # 3. RRF
    fused = reciprocal_rank_fusion([semantic_docs, bm25_results], k=60)
    top_ids = [doc_id for doc_id, _ in fused[:top_k]]

    # 4. Собираем тексты
    id_to_doc = {doc["id"]: doc for doc in bm25_index_builder.corpus}
    final_docs = []
    sql_examples = []

    for doc_id in top_ids:
        if doc_id in id_to_doc:
            text = id_to_doc[doc_id]["text"]
            doc_type = id_to_doc[doc_id]["metadata"]["type"]
            final_docs.append(text)
            if doc_type == "sql_example":
                sql_examples.append(text)

    return {
        "docs": final_docs,
        "sql_examples": sql_examples,
        "raw_results": top_ids
    }