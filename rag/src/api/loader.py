import os
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from docx import Document as DocxDocument
import fitz


from src.utils.kb_loader import kb_loader

app = FastAPI()
chroma_client, embedding_fn = kb_loader.chroma_client, kb_loader.embedding_fn

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # твой фронтенд (React, Vite и т.д.)
        "http://127.0.0.1:3000",
        # Добавь другие origins, если нужно (например, прод-домен)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # или ["POST", "GET"] — но для загрузки файлов нужен POST
    allow_headers=["*"],  # особенно важно для multipart/form-data
)

# Базовая директория для загрузок (лучше вынести в .env)
BASE_DIR = Path(__file__).parents[2] # /rag - на 2 уровня выше
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)

def safe_join(base: Path, subpath: str) -> Path:
    """Защита от path traversal (например, '../../etc/passwd')"""
    resolved = (base / subpath).resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise HTTPException(status_code=400, detail="Invalid folder path")
    return resolved

@app.post("/upload/")
async def upload_files(
    files: list[UploadFile] = File(...),
    folder: str = Form(default="default")
):
    # Нормализуем путь к папке (убираем лишние слэши и т.п.)
    folder = folder.strip("/").replace("\\", "/")
    if not folder:
        folder = "default"

    # Формируем безопасный путь
    target_dir = safe_join(KNOWLEDGE_BASE_DIR, folder)
    target_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []
    for file in files:
        if file.filename:
            file_path = target_dir / file.filename
            content = await file.read()

            # Сохраняем на диск в папку knowledge_base
            file_path = target_dir / file.filename
            with open(file_path, "wb") as f:
                f.write(content)
                saved_files.append(str(file_path.relative_to(KNOWLEDGE_BASE_DIR)))

            # Сохранем в хрому
            kb_loader.load_file(content, file.filename, doc_type=folder)

    for collection in ['t2t_docs', 'docs', 'sql_examples']:
        try:
            collection = chroma_client.get_collection(name=collection)
            all_data = collection.get()

            # Логи по коллекциям после загрузки дока
            print("IDs:", all_data['ids'])
            print("Documents:", all_data['documents'])
            print("Metadatas:", all_data['metadatas'])
            print("Embeddings count:", len(all_data['embeddings']) if all_data['embeddings'] else 0)
        except Exception as e:
            print('\nEXCEPTION', e)

    return JSONResponse(
        content={
            "message": f"Successfully uploaded {len(saved_files)} files",
            "folder": folder,
            "files": saved_files
        },
        status_code=201
    )