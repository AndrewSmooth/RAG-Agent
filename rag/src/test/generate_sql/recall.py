import sqlglot
from sqlglot import parse_one
from typing import Tuple, List

def extract_sqls(sql: str) -> Tuple[List[str], List[str]]:

    expr = parse_one(sql, dialect="duckdb")
    tables = list(expr.find_all(sqlglot.exp.Table))
    columns = list(expr.find_all(sqlglot.exp.Column))
    return (tables, columns)

def recall(truth_sql: str, generated_sql: str) -> float:

    truth_sqls = extract_sqls(truth_sql)
    generated_sqls = extract_sqls(generated_sql)

    tp_tables = 0
    for table in generated_sqls[0]:
        if table in truth_sqls[0]:
            tp_tables += 1
    
    tp_columns = 0
    for column in generated_sqls[1]:
        if column in truth_sqls[1]:
            tp_columns += 1
    
    return (tp_columns + tp_tables) / (len(truth_sqls[0]) + len(truth_sqls[1]))

if __name__ == "__main__":
    truth = """
    SELECT users.name, users.age, orders.total 
    FROM users 
    JOIN orders ON users.id = orders.user_id 
    WHERE users.city = 'Moscow' AND orders.status = 'shipped'        
    """
    generated = """
    SELECT users.name, users.age, orders.total 
    FROM users 
    JOIN orders ON users.id = orders.user_id 
    WHERE users.city_1 = 'Moscow' AND orders.status = 'shipped' AND users.status = 'canceled'   
    """
    print(extract_sqls(truth))

    print(recall(truth, generated))
