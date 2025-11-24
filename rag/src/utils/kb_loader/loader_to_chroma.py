from .loader import KnowledgeBaseLoader
from rag.src.utils.clients import get_chroma_client


def load_knowledge_base_to_chroma(
    kb_path: str,
    chroma_url: str,
    yandex_api_key: str,
    yandex_folder_id: str
):
    # 1. Загрузка файлов
    loader = KnowledgeBaseLoader(kb_path)
    t2t_docs = loader.load_t2t_docs()
    docs = loader.load_docs()
    sql_examples = loader.load_sql_examples()

    # 2. Подключение к Chroma
    chroma_client, embedding_fn = get_chroma_client(
        chroma_url=chroma_url,
        yandex_api_key=yandex_api_key,
        yandex_folder_id=yandex_folder_id
    )

    # 3. Создание/обновление коллекций

    # --- Коллекция: docs ---
    collection_docs = chroma_client.get_or_create_collection(
        name="docs",
        embedding_function=embedding_fn
    )

    collection_docs.add(
        ids=[f"doc_{i}" for i in range(len(docs))],
        documents=[doc.page_content for doc in docs],
        metadatas=[doc.metadata for doc in docs]
    )

    # --- Коллекция: sql_examples ---
    collection_sql = chroma_client.get_or_create_collection(
        name="sql_examples",
        embedding_function=embedding_fn
    )

    collection_sql.add(
        ids=[f"sql_{i}" for i in range(len(sql_examples))],
        documents=[doc.page_content for doc in sql_examples],
        metadatas=[doc.metadata for doc in sql_examples]
    )


    # Коллекция t2t_docs
    # chroma_client.delete_collection("t2t_docs") - очистка перед добавлением
    collection_t2t_docs = chroma_client.get_or_create_collection(
        name="t2t_docs",
        embedding_function=embedding_fn
    )

    test_documents = [doc.page_content for doc in t2t_docs]
    test_docs = [doc.metadata for doc in t2t_docs]


    collection_t2t_docs.add(
        ids=[f"t2t_doc_{i}" for i in range(len(t2t_docs))],
        documents=test_documents,
        metadatas=test_docs
    )
    collection_t2t_docs.get()

    print("✅ База знаний загружена в удалённый Chroma")

if __name__ == "__main__":

    

    import chromadb

    # Подключение к Chroma DB через HTTP (если она запущена с API)
    client = chromadb.HttpClient(host="localhost", port=8016)  # порт зависит от docker-compose

    # Посмотреть все коллекции
    collections = client.list_collections()
    print("Коллекции:", collections)

    # Выбери нужную коллекцию
    if collections:
        collection = client.get_collection(collections[0].name)
        print("Размер коллекции:", collection.count())

        # Посмотреть несколько примеров
        results = collection.peek(limit=5)  # или .get() для всех
        print("Примеры данных:", results)
