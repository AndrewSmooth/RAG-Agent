
schema = """
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name TEXT,
    location TEXT
);

CREATE TABLE employees (
    id INT PRIMARY KEY,
    name TEXT,
    age INT,
    salary REAL,
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(id)
);
"""

knowledge_base = [
    {
        "question": "List all employees",
        "sql": "SELECT * FROM employees;"
    },
    {
        "question": "Find employees earning more than 50000",
        "sql": "SELECT * FROM employees WHERE salary > 50000;"
    },
    {
        "question": "Show employee names and their department names",
        "sql": "SELECT e.name, d.name FROM employees e JOIN departments d ON e.dept_id = d.id;"
    },
    {
        "question": "How many employees are in each department?",
        "sql": "SELECT d.name, COUNT(*) FROM departments d JOIN employees e ON d.id = e.dept_id GROUP BY d.name;"
    },
    {
        "question": "Find the highest paid employee",
        "sql": "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 1;"
    }
]
