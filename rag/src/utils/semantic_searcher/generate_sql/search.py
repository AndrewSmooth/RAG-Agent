def search_in_knowledge_base(
    query: str,
    chroma_client,
    embedding_fn,
    k_docs=3,
    k_sql=3
):
    collection_docs = chroma_client.get_or_create_collection("docs", embedding_function=embedding_fn)
    collection_sql = chroma_client.get_or_create_collection("sql_examples", embedding_function=embedding_fn)

    results_docs = collection_docs.query(query_texts=[query], n_results=k_docs)
    results_sql = collection_sql.query(query_texts=[query], n_results=k_sql)

    # print("search_in_knowledge_base")
    # print(results_docs, results_sql)

    context = {
        "docs": results_docs["documents"][0] if results_docs["documents"] else [],
        "sql_examples": results_sql["documents"][0] if results_sql["documents"] else []
    }

    return context