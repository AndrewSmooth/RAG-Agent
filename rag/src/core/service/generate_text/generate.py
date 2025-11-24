from rag.src.utils.semantic_searcher.generate_text.search import search_in_knowledge_base
from rag.src.utils.prompts.generate_text.prompt import RAG_PROMPT_TEMPLATE
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from langchain_core.runnables import RunnableLambda

class GenerateTextService:

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
        t2t_docs = context["t2t_docs"] if context["t2t_docs"] else ["No relevant t2t_documents found"]
        formatted_context = "\n\n".join(t2t_docs)
        
        # Create prompt
        prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        
        # Create chain
        rag_chain = (
            {
                "context": RunnableLambda(lambda _: formatted_context),
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm_client
            | StrOutputParser()
        )
        
        # Invoke chain
        return rag_chain.invoke(query)