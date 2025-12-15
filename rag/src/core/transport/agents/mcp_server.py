import logging
from fastmcp import FastMCP
from ..core.t2t_service import search_knowledge_base
from ..core.t2sql_service import SQLService
from psycopg import Connection

from ...service import GenerateService


def create_mcp_app(sql_service, db_conn: Connection) -> FastMCP:
    mcp = FastMCP("RAG Agent 🧠📊")
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    # Раскоментировать для логов fastmcp. Может быть полезно при ошибках

    sql_service = SQLService(sql_service, db_conn)

    # --- T2T Tool ---
    @mcp.tool
    def search_knowledge_base_tool(query: str) -> str:
        """Ищи информацию в документации и базе знаний."""
        try:
            docs = search_knowledge_base(query)
            return "\n\n".join(docs) if docs else "Не найдено релевантной информации."
        except Exception as e:
            return f"Ошибка поиска: {str(e)}"

    # --- T2SQL Tools ---
    @mcp.tool
    def generate_sql(question: str) -> str:
        """Сгенерируй SQL-запрос по вопросу на естественном языке."""
        try:
            return sql_service.generate_sql(question).strip()
        except Exception as e:
            return f"-- ОШИБКА генерации SQL: {str(e)}"

    @mcp.tool
    def run_sql_safely(sql: str) -> dict:
        """Выполни безопасный SELECT-запрос и верни результаты."""
        return sql_service.run_sql_safely(sql)

    return mcp


def run_mcp_server(
        sql_service: GenerateService,
        db_conn: Connection,
        host: str = "0.0.0.0",
        port: int = 8008
    ):

    app = create_mcp_app(sql_service, db_conn)
    app.run(transport="http", host=host, port=port)