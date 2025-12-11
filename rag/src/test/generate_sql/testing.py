import os
import json
import random

from dotenv import load_dotenv

from src.test.generate_sql.recall import recall
from src.core.service.generate_sql.generate import GenerateSQLService
from src.utils.clients.embedding_client import get_chroma_client
from langchain_openai import ChatOpenAI

def load_random_sql_examples(folder_path, num_files=10):
    
    try:
        json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    except FileNotFoundError:
        raise FileNotFoundError(f"Папка не найдена: {folder_path}")
    except Exception as e:
        raise Exception(f"Ошибка при чтении папки: {e}")

    if len(json_files) < num_files:
        print(f"Внимание: найдено только {len(json_files)} файлов (запрошено {num_files}). Будут использованы все.")

    selected_files = random.sample(json_files, min(num_files, len(json_files)))

    result = []

    for filename in selected_files:
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'question' in data and 'sql' in data:
                    result.append({
                        'question': data['question'],
                        'sql': data['sql'],
                        'source_file': filename
                    })
                else:
                    print(f"Пропущен файл {filename}: отсутствуют необходимые поля.")
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON в файле {filename}: {e}")
        except Exception as e:
            print(f"Ошибка при чтении файла {filename}: {e}")

    return result

if __name__ == "__main__":
    folder = "knowledge_base/sql_examples"
    examples = load_random_sql_examples(folder, 10)

    load_dotenv()
    
    # Get environment variables
    yandex_api_key = os.getenv("YANDEX_CLOUD_API_KEY")
    yandex_folder_id = os.getenv("YANDEX_CLOUD_FOLDER")
    
    # Create chroma client and embedding function
    chroma_client, embedding_fn = get_chroma_client(
        yandex_api_key=yandex_api_key,
        yandex_folder_id=yandex_folder_id
    )
    
    # Create LLM client
    llm = ChatOpenAI(
        api_key=yandex_api_key,
        base_url="https://llm.api.cloud.yandex.net/v1",
        model=f"gpt://{yandex_folder_id}/yandexgpt-lite",
        temperature=0.1,
        max_tokens=2000,
    )
    # The actual logic is now in setup.py which serves as the main entry point
    # This file can be used for simple demonstrations or testing
    # Create SQL generation service
    generate_sql_service = GenerateSQLService(chroma_client, embedding_fn, llm)
    

    metric_sum = 0
    for i, ex in enumerate(examples, 1):
        generated_sql = generate_sql_service.generate(ex['question'])
        print(f"{i}. Вопрос: {ex['question']}")
        print(f"   SQL: {ex['sql']}\n")
        print(f"   Generated SQL: {generated_sql}")

        metric_sum += recall(ex['sql'], generated_sql)
    metric = metric_sum / len(examples)

    print(f"Итоговая метрика: {metric}")

