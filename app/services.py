import time
import os
import json
import asyncio
import requests
from typing import Tuple, List

from fastapi import HTTPException, UploadFile
from dotenv import load_dotenv

from schemas import QuestionRequest
from config import DATA_DIR
from utils import chunk_by_heading1, get_base64_by_id
from prompt import llm_prompt
from inference import generate_response


load_dotenv()
UPSTAGE_API_KEY = os.environ.get("UPSTAGE_API_KEY")
UPSTAGE_API_URL = os.environ.get("UPSTAGE_API_URL")


def get_data_file_path(doc_name: str) -> str:
    return os.path.join(DATA_DIR, f"{doc_name}.json")


def process_pdf(doc_name: str, file: UploadFile, chroma_client, model_manager) -> None:
    files = {
        "document": (file.filename, file.file, file.content_type)
    }
    data = {
        "ocr": "force",
        "base64_encoding": "['figure']",
        "model": "document-parse"
    }
    headers = {
        "Authorization": f"Bearer {UPSTAGE_API_KEY}"
    }

    try:
        response = requests.post(UPSTAGE_API_URL, headers=headers, files=files, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstage API Error: {str(e)}")
    
    response_data = response.json()

    with open(get_data_file_path(doc_name), "w", encoding="utf-8") as f:
        json.dump(response_data, f, ensure_ascii=False, indent=4)

    chunks = chunk_by_heading1(response_data['elements'])

    documents = []
    metadatas = []
    ids = []

    for i, chunk in enumerate(chunks):
        section = chunk["section_heading"]
        for elem in chunk["elements"]:
            doc_id = f"{i}_{elem['id']}"
            doc = f"[그림: '{section}' 섹션에 해당하는 시각 자료입니다.]" if elem["category"] == "figure" else elem["text"]

            documents.append(doc)
            ids.append(doc_id)
            metadatas.append({
                "section": section,
                "category": elem["category"],
                "page": elem["page"],
                "element_id": elem["id"]
            })

    collection = chroma_client.get_or_create_collection(doc_name)
    embeddings = model_manager.sentence_model.encode(documents).tolist()

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )


async def get_llm_answer(request: QuestionRequest, chroma_client, model_manager) -> Tuple[str, List[str]]:
    start_time = time.time()

    doc_name = request.doc_name
    query = request.question

    collection = chroma_client.get_or_create_collection(doc_name)
    query_embedding = model_manager.sentence_model.encode([query])[0].tolist()

    results = collection.query(query_embeddings=[query_embedding], n_results=5)
    context = "\n\n".join(results['documents'][0])
    prompt = llm_prompt(query, context)

    answer = await generate_response(prompt)

    try:
        """
        작은 파일이므로 blocking 함수 open 사용
        만약 파일이 크다면, aiofiles 라이브러리(비동기 파일 입출력 기능) 사용 고려
        """
        with open(get_data_file_path(doc_name), "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document data not found.")

    images = [
        get_base64_by_id(data["elements"], m["element_id"])
        for m in results['metadatas'][0] if m["category"] == "figure"
    ]

    processing_time = round(time.time() - start_time, 2)
    print(f"processing_time: {processing_time}")

    return answer, images
