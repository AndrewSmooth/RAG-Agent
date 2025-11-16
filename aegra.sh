#!/bin/bash

# Запуск аегры в докере

cd aegra
# инициализация окружения
uv sync
source .venv/bin/activate


# запуск через docker
docker compose up postgres -d  # только БД
docker compose up aegra        # сервис с миграциями

# проверка
curl http://localhost:8000/health
# {"status":"healthy"}