import bs4
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class KnowledgeBaseLoader:
    """
    Класс для загрузки ресурсов в векторное хранилище. Использует хранилище в оперативной памяти
    """

    def __init__(self, embedding_model=None, load_test_data=False):
        if embedding_model is None:
            # Только cpu т.к. В requirements устанавливаем torch без cuda для меньшего размера
            embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={"device": "cpu"} )
        self.vector_store = InMemoryVectorStore(embedding_model)

        if load_test_data:
            urls = [
                'https://vc.ru/apple/2459924-apple-izmenit-grafik-relizov-i-vypustit-do-shesti-novykh-iphone',
                'https://vc.ru/apple/2448822-apple-obyazana-vyplatit-masimo-634-mln-za-narushenie-patenta',
                'https://vc.ru/id5478280/2448726-pensiia-dlia-zumerov-i-millienialov-pochemu-ei-ne-budut'
            ]
            self._add_from_vc_ru(*urls)
        print()

    def _add_from_vc_ru(self, *urls: str) -> None:
        """
        Добавляет в векторное хранилище данные из одной или нескольких веб-страниц с vc.ru.
        Принимает один или несколько URL
        """
        if not urls:
            return

        loader = WebBaseLoader(
            web_paths=urls,
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(
                    class_='content'
                )
            ),
        )
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)

        self.vector_store.add_documents(documents=all_splits)

    def find_doc_by_query(self, query: str) -> list[Document]:
        """Ищет документ по запросу"""
        return self.vector_store.similarity_search(query)
