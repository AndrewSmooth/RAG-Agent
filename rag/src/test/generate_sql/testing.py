import os
import json
import random
from datetime import datetime
import httpx
import csv
from pathlib import Path

from dotenv import load_dotenv

from src.test.generate_sql.recall import recall
from src.utils.clients.embedding_client import get_chroma_client
from langchain_openai import ChatOpenAI

# Импортируем различные реализации сервисов генерации SQL
from src.core.service.generate_sql.hybrid.src import GenerateSQLService as HybridGenerateSQLService
from src.core.service.generate_sql.hybrid_with_prompting.src import GenerateSQLService as HybridWithPromptingGenerateSQLService
from src.core.service.generate_sql.only_semantic.src import GenerateSQLService as OnlySemanticGenerateSQLService
from src.utils.kb_loader.loader import KnowledgeBaseLoader

def load_testing(file_path, num_examples=20):
    """Загружает указанное количество примеров из JSON файла."""
    with open(file_path, "r") as file:
        content = file.read()
    examples = json.loads(content)
    if num_examples >= len(examples):
        print(f"Запрошено {num_examples} примеров, но доступно только {len(examples)}. Используем все.")
        return examples
    sampled_examples = random.sample(examples, num_examples)
    return sampled_examples

def create_service(service_type, chroma_client, embedding_fn, llm, kb_loader):
    """Создает экземпляр сервиса генерации SQL в зависимости от типа."""
    if service_type == "hybrid":
        return HybridGenerateSQLService(chroma_client, embedding_fn, llm, kb_loader)
    elif service_type == "hybrid_with_prompting":
        return HybridWithPromptingGenerateSQLService(chroma_client, embedding_fn, llm, kb_loader)
    elif service_type == "only_semantic":
        return OnlySemanticGenerateSQLService(chroma_client, embedding_fn, llm)
    else:
        raise ValueError(f"Неизвестный тип сервиса: {service_type}")

def evaluate_service(service, examples, service_name):
    """Оценивает производительность сервиса на наборе примеров."""
    metric_sum = 0
    results = []
    
    print(f"\n{'='*50}")
    print(f"Оценка сервиса: {service_name}")
    print(f"{'='*50}")
    
    for i, ex in enumerate(examples, 1):
        start_time = datetime.now()
        generated_sql = service.generate(ex['question'])
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        recall_score = recall(ex['sql'], generated_sql)
        metric_sum += recall_score
        
        results.append({
            'question': ex['question'],
            'true_sql': ex['sql'],
            'generated_sql': generated_sql,
            'recall': recall_score,
            'generation_time': generation_time
        })
        
        print(f"{i}. Вопрос: {ex['question']}")
        print(f"   Истинный SQL: {ex['sql']}")
        print(f"   Сгенерированный SQL: {generated_sql}")
        print(f"   Recall: {recall_score:.4f}")
        print(f"   Время генерации: {generation_time:.2f} сек")
        print()
    
    avg_recall = metric_sum / len(examples) if examples else 0
    avg_time = sum(r['generation_time'] for r in results) / len(results) if results else 0
    
    print(f"Итоговая метрика Recall: {avg_recall:.4f}")
    print(f"Среднее время генерации: {avg_time:.2f} сек")
    
    return {
        'service_name': service_name,
        'avg_recall': avg_recall,
        'avg_time': avg_time,
        'results': results
    }

if __name__ == "__main__":
    # Загружаем переменные окружения
    load_dotenv()
    
    # Получаем переменные окружения
    yandex_api_key = os.getenv("YANDEX_CLOUD_API_KEY")
    yandex_folder_id = os.getenv("YANDEX_CLOUD_FOLDER")
    openapi_key = os.getenv("OPENAIAPI_KEY")
    
    # Создаем клиент Chroma и функцию эмбеддингов
    chroma_client, embedding_fn = get_chroma_client(
        yandex_api_key=yandex_api_key,
        yandex_folder_id=yandex_folder_id
    )

    http_client = httpx.Client(verify=False)
    
    # Создаем LLM клиент
    llm = ChatOpenAI(
        api_key=openapi_key,
        base_url="https://api.eliza.yandex.net/raw/openai/v1",
        model="gpt-4",
        temperature=0.1,
        max_tokens=700,
        http_client=http_client,
    )
    
    # Создаем загрузчик базы знаний
    kb_loader = KnowledgeBaseLoader(
        kb_path="knowledge_base",
        chroma_url="http://localhost:8000",
        yandex_api_key=yandex_api_key,
        yandex_folder_id=yandex_folder_id
    )
    
    # Определяем размеры выборок для тестирования
    sample_sizes = [5, 20, 50]
    test_file = "knowledge_base/test/sql1.json"
    
    # Определяем типы сервисов для тестирования
    service_types = [
        ("hybrid", "Hybrid Search"),
        ("hybrid_with_prompting", "Hybrid with Prompting"),
        ("only_semantic", "Only Semantic Search")
    ]
    
    # Собираем результаты для всех комбинаций
    all_results = []
    
    for size in sample_sizes:
        print(f"\n{'#'*60}")
        print(f"ТЕСТИРОВАНИЕ НА ВЫБОРКЕ ИЗ {size} ПРИМЕРОВ")
        print(f"{'#'*60}")
        
        # Загружаем примеры
        examples = load_testing(test_file, size)
        print(f"Загружено {len(examples)} примеров для тестирования")
        
        # Тестируем каждый тип сервиса
        for service_type, service_name in service_types:
            service = create_service(service_type, chroma_client, embedding_fn, llm, kb_loader)
            result = evaluate_service(service, examples, service_name)
            result['sample_size'] = size
            all_results.append(result)
    
    # Выводим сводную таблицу результатов
    print(f"\n{'='*80}")
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print(f"{'='*80}")
    print(f"{'Размер выборки':<15} {'Сервис':<25} {'Recall':<10} {'Время (сек)':<12}")
    print(f"{'-'*80}")
    
    for result in all_results:
        print(f"{result['sample_size']:<15} {result['service_name']:<25} {result['avg_recall']:<10.4f} {result['avg_time']:<12.2f}")
    
    # Выводим анализ результатов
    print(f"\n{'='*80}")
    print("АНАЛИЗ РЕЗУЛЬТАТОВ")
    print(f"{'='*80}")
    
    # Группируем результаты по сервисам
    services_data = {}
    for result in all_results:
        service_name = result['service_name']
        if service_name not in services_data:
            services_data[service_name] = []
        services_data[service_name].append(result)
    
    for service_name, data in services_data.items():
        print(f"\n{service_name}:")
        print(f"  Зависимость Recall от размера выборки:")
        for item in sorted(data, key=lambda x: x['sample_size']):
            print(f"    {item['sample_size']} примеров: {item['avg_recall']:.4f}")
        
        # Анализ тренда
        if len(data) > 1:
            recalls = [item['avg_recall'] for item in sorted(data, key=lambda x: x['sample_size'])]
            if recalls[-1] > recalls[0]:
                trend = "улучшается с увеличением выборки"
            elif recalls[-1] < recalls[0]:
                trend = "ухудшается с увеличением выборки"
            else:
                trend = "стабилен при изменении размера выборки"
            print(f"  Общая тенденция: {trend}")
    
    # Создаем директорию для результатов
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Сохраняем сводные результаты в CSV
    summary_csv_path = results_dir / "summary_results.csv"
    with open(summary_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_size", "service_name", "avg_recall", "avg_time"])
        for result in all_results:
            writer.writerow([
                result["sample_size"],
                result["service_name"],
                result["avg_recall"],
                result["avg_time"]
            ])
    print(f"\nСводные результаты сохранены в {summary_csv_path}")
    
    # Сохраняем детальные результаты для каждого теста
    for result in all_results:
        service_name_safe = result["service_name"].replace(" ", "_").lower()
        sample_size = result["sample_size"]
        detail_csv_path = results_dir / f"details_{service_name_safe}_{sample_size}.csv"
        
        with open(detail_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["question", "true_sql", "generated_sql", "recall", "generation_time"])
            for item in result["results"]:
                writer.writerow([
                    item["question"],
                    item["true_sql"],
                    item["generated_sql"],
                    item["recall"],
                    item["generation_time"]
                ])
        print(f"Детальные результаты для {result['service_name']} ({sample_size} примеров) сохранены в {detail_csv_path}")
