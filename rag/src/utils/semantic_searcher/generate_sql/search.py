# src/utils/semantic_searcher/generate_sql.py

def search_in_knowledge_base(query: str, chroma_client, embedding_fn, top_k=5):
    # Получаем коллекции
    collection_docs = chroma_client.get_collection("docs")        # или другое имя
    collection_sql = chroma_client.get_collection("sql_examples") # или другое имя

    # Поиск по документации
    results_docs = collection_docs.query(
        query_embeddings=embedding_fn([query]),
        n_results=top_k
    )

    # Поиск по SQL-примерам
    results_sql = collection_sql.query(
        query_embeddings=embedding_fn([query]),
        n_results=top_k
    )

    # Собираем ID и расстояния
    all_ids = []
    all_distances = []

    # Добавляем из docs
    if results_docs["ids"]:
        all_ids.extend(results_docs["ids"][0])
        all_distances.extend(results_docs["distances"][0])

    # Добавляем из sql_examples
    if results_sql["ids"]:
        all_ids.extend(results_sql["ids"][0])
        all_distances.extend(results_sql["distances"][0])

    # Убираем дубли (по ID), сохраняя лучшее расстояние
    unique_results = {}
    for doc_id, distance in zip(all_ids, all_distances):
        if doc_id not in unique_results or distance < unique_results[doc_id]:
            unique_results[doc_id] = distance

    # Сортируем по расстоянию (лучшие — ближе)
    sorted_pairs = sorted(unique_results.items(), key=lambda x: x[1])
    top_pairs = sorted_pairs[:top_k]

    top_ids = [pair[0] for pair in top_pairs]
    top_distances = [pair[1] for pair in top_pairs]

    # Собираем документы в том же порядке
    id_to_doc = {}
    for i, doc_id in enumerate(results_docs["ids"][0] if results_docs["ids"] else []):
        id_to_doc[doc_id] = results_docs["documents"][0][i]
    for i, doc_id in enumerate(results_sql["ids"][0] if results_sql["ids"] else []):
        id_to_doc[doc_id] = results_sql["documents"][0][i]

    top_documents = [id_to_doc[doc_id] for doc_id in top_ids if doc_id in id_to_doc]

    # Возвращаем ВСЁ, что нужно для гибридного поиска
    return {
        "documents": top_documents,
        "ids": top_ids,
        "distances": top_distances
    }
