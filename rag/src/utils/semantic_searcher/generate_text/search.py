def search_in_knowledge_base(
    query: str,
    chroma_client,
    embedding_fn,
    k_docs=3
):
    collection_t2t_docs = chroma_client.get_or_create_collection("docs", embedding_function=embedding_fn)
    results_t2t_docs = collection_t2t_docs.query(query_texts=[query], n_results=k_docs)

    context = {
        "docs": results_t2t_docs["documents"][0] if results_t2t_docs["documents"] else []
    }

    return context