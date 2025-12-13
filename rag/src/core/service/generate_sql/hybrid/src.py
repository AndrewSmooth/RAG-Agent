from src.utils.bm25_index_builder import BM25IndexBuilder
from .hybrid_searcher import hybrid_search
from src.utils.prompts.generate_sql import RAG_SQL_PROMPT_TEMPLATE
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

class GenerateSQLService:
    def __init__(
        self,
        chroma_client,
        embedding_fn,
        llm_client,
        kb_loader  # <-- только для BM25IndexBuilder
    ):
        self.chroma_client = chroma_client
        self.embedding_fn = embedding_fn
        self.llm_client = llm_client

        # Строим BM25 индекс, используя kb_loader, НО не изменяя его
        self.bm25_index_builder = BM25IndexBuilder(kb_loader).build_index()

    def generate(self, query: str):
        context = hybrid_search(
            query=query,
            chroma_client=self.chroma_client,
            embedding_fn=self.embedding_fn,
            bm25_index_builder=self.bm25_index_builder,
            top_k=5
        )

        sql_examples = context["sql_examples"] if context["sql_examples"] else ["No SQL examples found"]
        docs = context["docs"] if context["docs"] else ["No documentation found"]
        all_context = sql_examples + docs
        formatted_context = "\n\n".join(all_context)

        prompt = ChatPromptTemplate.from_template(RAG_SQL_PROMPT_TEMPLATE)

        rag_chain = (
            {
                "sql_schema": RunnableLambda(lambda _: docs),
                "context": RunnableLambda(lambda _: formatted_context),
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm_client
            | StrOutputParser()
        )

        return rag_chain.invoke(query)