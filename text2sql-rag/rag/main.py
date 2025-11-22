from src.core import GenerateService

def main():
    # The actual logic is now in setup.py which serves as the main entry point
    # This file can be used for simple demonstrations or testing
    generate_service = GenerateService()  # This would need to be properly initialized
    user_question = "Show all employees in the Engineering department"
    generated_sql = generate_service.generate(user_question)
    print(f"Question: {user_question}")
    print(f"Generated SQL: {generated_sql}")

if __name__ == "__main__":
    main()
