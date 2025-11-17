from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

from embeddings import YandexCloudEmbeddings
from base import schema, knowledge_base
from prompt import RAG_PROMPT_TEMPLATE
load_dotenv()

YANDEX_CLOUD_API_KEY = os.getenv("YANDEX_CLOUD_API_KEY")
YANDEX_CLOUD_FOLDER = os.getenv("YANDEX_CLOUD_FOLDER")


embeddings = YandexCloudEmbeddings(
    api_key=YANDEX_CLOUD_API_KEY,
    folder_id=YANDEX_CLOUD_FOLDER
)

documents = [
    Document(page_content=f"Question: {ex['question']}\nSQL: {ex['sql']}")
    for ex in knowledge_base
]

vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings  # ← используем кастомные эмбеддинги
)

retriever = vectorstore.as_retriever(k=2)


prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
llm = ChatOpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://llm.api.cloud.yandex.net/v1",
    model=f"gpt://{YANDEX_CLOUD_FOLDER}/yandexgpt-lite",
    temperature=0.1,
    max_tokens=2000,
)

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

rag_chain = (
    {"sql_schema": schema, "context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def text_to_sql(question: str) -> str:
    return rag_chain.invoke(question)

# Пример использования
if __name__ == "__main__":
    user_question = "Show all employees in the Engineering department"
    generated_sql = text_to_sql(user_question)
    print(f"Question: {user_question}")
    print(f"Generated SQL: {generated_sql}")
