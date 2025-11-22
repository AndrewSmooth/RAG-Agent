

def search_in_knowledge_base(
    query: str,
    chroma_client,
    embedding_fn,
    k_docs=3,
    k_sql=3
):

    collection_docs = chroma_client.get_collection("docs", embedding_function=embedding_fn)
    collection_sql = chroma_client.get_collection("sql_examples", embedding_function=embedding_fn)

    results_docs = collection_docs.query(query_texts=[query], n_results=k_docs)
    results_sql = collection_sql.query(query_texts=[query], n_results=k_sql)

    context = {
        "docs": results_docs["documents"][0] if results_docs["documents"] else [],
        "sql_examples": results_sql["documents"][0] if results_sql["documents"] else []
    }

    return context

if __name__ == "__main__":

    from dotenv import load_dotenv
    import os

    load_dotenv()

    YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
    YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER")
    search_in_knowledge_base(
        "how to get all employees",
        "http://localhost:8016",
        YANDEX_CLOUD_API_KEY,
        YANDEX_CLOUD_FOLDER
    )