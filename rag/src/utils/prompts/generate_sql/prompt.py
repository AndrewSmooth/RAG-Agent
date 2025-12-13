RAG_SQL_PROMPT_TEMPLATE = """
You are an expert in converting natural language questions into SQL queries.
Use the following examples to guide your response.

SQL: {sql_schema}
Examples:
{context}

Now, convert the following question into a SQL query.
Ensure:
- Only output valid SQL.
- Use table names: 'employees' and 'departments'.
- Use proper JOINs when needed.
- Do not include explanations.

Question: {question}
"""