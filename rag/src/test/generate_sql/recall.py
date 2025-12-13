import sqlglot
from sqlglot import parse_one
from typing import Set, Tuple

def extract_tables_and_columns(sql: str, dialect: str = "mysql") -> Tuple[Set[str], Set[str]]:
    """
    Возвращает:
        - Множество таблиц: {'users', 'orders'}
        - Множество колонок: {'users.id', 'users.name', 'orders.status'}
    """

    sql = sql.strip().strip('`"\'')
    try:
        expr = parse_one(sql, dialect)
    except Exception as e:
        print(f"Parse error: {e}")
        return set(), set()

    tables = set()
    columns = set()

    # Извлекаем таблицы
    for table in expr.find_all(sqlglot.exp.Table):
        table_name = table.name.lower()  # например, 'users'
        tables.add(table_name)

    # Извлекаем колонки
    for col in expr.find_all(sqlglot.exp.Column):
        col_name = col.name.lower()
        table_name = col.table.lower() if col.table else None
        if table_name:
            columns.add(f"{table_name}.{col_name}")
        else:
            columns.add(col_name)  # без таблицы

    return tables, columns


def recall(truth_sql: str, generated_sql: str, dialect: str = "mysql") -> float:
    truth_tables, truth_cols = extract_tables_and_columns(truth_sql, dialect)
    gen_tables, gen_cols = extract_tables_and_columns(generated_sql, dialect)

    # Нормализуем: для сравнения колонок — разрешаем совпадение по имени
    truth_col_names = {col.split('.')[-1] for col in truth_cols if not col in truth_tables}
    gen_col_names = {col.split('.')[-1] for col in gen_cols if not col in gen_tables}

    # Таблицы: просто пересечение
    tp_tables = len(truth_tables & gen_tables)

    # Колонки: либо полное совпадение (table.col), либо по имени
    tp_columns = 0
    for col in gen_cols:
        if col in truth_cols:
            tp_columns += 1  # полное совпадение: e.salary == e.salary
        else:
            col_name = col.split('.')[-1]
            if col_name in truth_col_names and col_name not in gen_tables:
                tp_columns += 1  # совпадение по имени: e.salary → salary

    # Общее количество эталонных элементов
    generated_truth = len(gen_tables) + len(gen_cols)

    recall = (tp_tables + tp_columns) / generated_truth if generated_truth > 0 else 1.0

    print(f"Эталонные таблицы: {truth_tables}")
    print(f"Извлечённые таблицы: {gen_tables}")
    print(f"Совпавшие таблицы: {truth_tables & gen_tables}")

    print(f"Эталонные колонки: {truth_cols}")
    print(f"Извлечённые колонки: {gen_cols}")
    print(f"Совпавшие колонки (частично): {tp_columns}")

    return recall
