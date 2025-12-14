import re
from src.core.service import GenerateService
from typing import List, Dict, Any
from psycopg import Connection

class SQLService:

    def __init__(
            self,
            sql_service: GenerateService,
            db_conn: Connection,
    ):

        # Основной сервис генерации SQL
        self.sql_service = sql_service

        # Параметры подключения к БД
        self.db_conn = db_conn

    def generate_sql(
            self,
            question: str
    ) -> str:

        try:
            return "SELECT * FROM DUAL;"
            sql = self.sql_service.generate(question)
            return sql.strip()
        except Exception as e:
            return f"-- ОШИБКА при генерации SQL: {str(e)}"

    def run_sql_safely(
            self,
            sql: str
    ) -> Dict[str, Any]:

        # 1. Валидация: только SELECT, без опасных команд
        if not self._is_safe_select(sql):
            return {
                "error": "Запрещённый тип запроса. Разрешены только безопасные SELECT-запросы без модификации данных.",
                "allowed": False,
                "query": sql.strip()
            }

        # 2. Выполнение
        try:
            with self.db_conn.cursor() as cur:
                cur.execute(sql)
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()

                results = [dict(zip(columns, row)) for row in rows]

                return {
                    "success": True,
                    "query": sql.strip(),
                    "row_count": len(results),
                    "data": results[:100]  # Ограничиваем 100 строками
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка выполнения SQL: {str(e)}",
                "query": sql.strip()
                }

    def _is_safe_select(self, sql: str) -> bool:
        """
        Проверяет, что запрос — безопасный SELECT.
        Запрещает: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, BEGIN, COMMIT и т.д.
        """
        if not sql.strip():
            return False

        sql_lower = sql.strip().lower()

        # Должен начинаться с SELECT
        if not re.match(r'^\s*select\s+', sql_lower):
            return False

        # Запрещённые ключевые слова (даже в комментариях — на всякий случай)
        forbidden_keywords = [
            'insert', 'update', 'delete', 'drop', 'alter', 'truncate', 'create',
            'grant', 'revoke', 'shutdown', 'restart', 'vacuum',
            'begin', 'commit', 'rollback', 'lock', 'call'
        ]

        for keyword in forbidden_keywords:
            # Ищем как отдельные слова (через \b — word boundary)
            if re.search(r'\b' + re.escape(keyword) + r'\b', sql_lower):
                return False

        # Запрещаем подозрительные вещи
        if 'pg_sleep' in sql_lower or 'sleep(' in sql_lower:
            return False

        return True