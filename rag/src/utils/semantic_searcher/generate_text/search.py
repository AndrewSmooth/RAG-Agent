def search_in_knowledge_base(
    query: str,
    chroma_client,
    embedding_fn,
    k_docs=3
):
    collection_docs = chroma_client.get_collection("docs", embedding_function=embedding_fn)

    results_docs = collection_docs.query(query_texts=[query], n_results=k_docs)

    context = {
        "docs": results_docs["documents"][0] if results_docs["documents"] else []
    }

    return context