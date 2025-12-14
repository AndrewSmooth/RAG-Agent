cd rag
docker compose up -d
uvicorn src.api.loader:app --reload --port 8800