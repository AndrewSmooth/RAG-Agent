import re
from src.core.service import GenerateService
from typing import List, Dict, Any
from psycopg import Connection

class TextService:

    def __init__(
            self,
            text_service: GenerateService,
    ):

        # Основной сервис генерации SQL
        self.text_service = text_service

    def generate_text(
            self,
            question: str
    ) -> str:

        try:
            sql = self.text_service.generate(question)
            return sql.strip()
        except Exception as e:
            return f"-- ОШИБКА при генерации Text: {str(e)}"