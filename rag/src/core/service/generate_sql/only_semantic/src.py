
from src.utils.semantic_searcher.generate_sql import search_in_knowledge_base
from src.utils.prompts.generate_sql import RAG_SQL_PROMPT_TEMPLATE
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

class GenerateSQLService:

    def __init__(self, chroma_client, embedding_fn, llm_client):
        self.chroma_client = chroma_client
        self.embedding_fn = embedding_fn
        self.llm_client = llm_client

    def generate(self, query: str):
        # Search in knowledge base
        context = search_in_knowledge_base(
            query=query,
            chroma_client=self.chroma_client,
            embedding_fn=self.embedding_fn,
            top_k=3,
        )

        # Categorize documents based on their type
        docs = []
        sql_examples = []

        for doc, doc_type in zip(context["documents"], context.get("doc_types", [])):
            if doc_type == "sql_examples":
                sql_examples.append(doc)
            elif doc_type == "docs":
                docs.append(doc)

        # Handle case where doc_types is not available (backward compatibility)
        if not context.get("doc_types") and isinstance(context, dict) and "documents" in context:
            # Fallback to old behavior if doc_types is not present
            docs = context.get("docs", [])
            sql_examples = context.get("sql_examples", [])

        # Format context - handle empty results
        if not sql_examples:
            sql_examples = ["No SQL examples found"]
        if not docs:
            docs = ["No documentation found"]
        all_context = sql_examples + docs
        formatted_context = "\n\n".join(all_context)

        # Create prompt
        prompt = ChatPromptTemplate.from_template(RAG_SQL_PROMPT_TEMPLATE)
        
        # Create chain
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
        
        # Invoke chain
        return rag_chain.invoke(query)