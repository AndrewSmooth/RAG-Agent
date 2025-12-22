# src/services/generate_sql_service.py

from src.utils.query_enhancer import QueryEnhancer
from src.utils.bm25_index_builder import BM25IndexBuilder
from .hybrid_searcher import hybrid_search
from src.utils.prompts.generate_sql import RAG_SQL_PROMPT_TEMPLATE, RAG_SQL_HYBRID_TEMPLATE
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

class GenerateSQLService:
    def __init__(
        self,
        chroma_client,
        embedding_fn,
        llm_client,
        kb_loader
    ):
        self.chroma_client = chroma_client
        self.embedding_fn = embedding_fn
        self.llm_client = llm_client
        self.bm25_index_builder = BM25IndexBuilder(kb_loader).build_index()

        # Добавляем QueryEnhancer
        self.query_enhancer = QueryEnhancer(llm_client)

    def generate(self, query: str):
        # 1. Улучшаем запрос
        enhanced = self.query_enhancer.enhance(query)

        # 2. Используем переформулированный запрос для поиска
        search_query = enhanced["rewritten_query"]

        # 🔍 МОЖНО: использовать mentioned_tables для фильтрации в BM25/Chroma
        # Например: искать только в документах, где есть упоминание таблицы

        context = hybrid_search(
            query=search_query,  # ← улучшенный запрос
            chroma_client=self.chroma_client,
            embedding_fn=self.embedding_fn,
            bm25_index_builder=self.bm25_index_builder,
            top_k=5
        )

        sql_examples = context["sql_examples"] if context["sql_examples"] else ["No SQL examples found"]
        docs = context["docs"] if context["docs"] else ["No documentation found"]
        all_context = sql_examples + docs
        formatted_context = "\n\n".join(all_context)

        # 3. Передаём в промпт не только контекст, но и понимание запроса
        prompt = ChatPromptTemplate.from_template(RAG_SQL_PROMPT_TEMPLATE)

        rag_chain = (
            {
                "sql_schema": RunnableLambda(lambda _: docs),
                "context": RunnableLambda(lambda _: formatted_context),
                "question": RunnablePassthrough(),
                "rewritten_query": RunnableLambda(lambda _: enhanced["rewritten_query"]),
                "tables_hint": RunnableLambda(lambda _: ", ".join(enhanced["mentioned_tables"]) or "не определены"),
                "time_constraint": RunnableLambda(lambda _: enhanced["time_constraints"]),
                "aggregation": RunnableLambda(lambda _: enhanced["aggregation"])
            }
            | prompt
            | self.llm_client
            | StrOutputParser()
        )

        return rag_chain.invoke(query)
