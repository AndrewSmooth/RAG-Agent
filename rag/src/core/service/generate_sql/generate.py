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
            embedding_fn=self.embedding_fn
        )
        
        # Format context - handle empty results
        sql_examples = context["sql_examples"] if context["sql_examples"] else ["No SQL examples found"]
        docs = context["docs"] if context["docs"] else ["No documentation found"]
        all_context = sql_examples + docs
        formatted_context = "\n\n".join(all_context)

        # print(formatted_context)

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