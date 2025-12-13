# src/utils/query_enhancer.py

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field

class QueryUnderstanding(BaseModel):
    rewritten_query: str = Field(description="Переформулированный, более точный запрос")
    mentioned_tables: list = Field(default_factory=list, description="Предполагаемые таблицы")
    time_constraints: str = Field(default="", description="Временные условия")
    aggregation: str = Field(default="", description="Агрегация: COUNT, SUM, AVG и т.д.")
    filter_conditions: list = Field(default_factory=list, description="Условия фильтрации")

class QueryEnhancer:
    def __init__(self, llm):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=QueryUnderstanding)

        self.prompt = PromptTemplate.from_template(
            """
Вы — эксперт по преобразованию естественного языка в структурированные SQL-запросы.
Проанализируй вопрос и верни структурированную информацию.

Доступные таблицы (для подсказки):
{schema_hint}

Вопрос: {question}

{format_instructions}
            """
        ).partial(
            format_instructions=self.parser.get_format_instructions(),
            schema_hint="users, orders, products, user_activity"  # ← можно подгружать динамически
        )

        self.chain = self.prompt | self.llm | self.parser

    def enhance(self, query: str) -> dict:
        try:
            result = self.chain.invoke({"question": query})
            return result
        except Exception as e:
            # На случай ошибки парсинга
            return {
                "rewritten_query": query,
                "mentioned_tables": [],
                "time_constraints": "",
                "aggregation": "",
                "filter_conditions": []
            }
