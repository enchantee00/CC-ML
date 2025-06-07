import asyncio
import httpx
import time
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("API_KEY")

questions = [
    "제품 설치는 사용자가 직접 해도 되나요?",
    "캠핑카나 선박 등에 설치해도 되나요?",
    "어떤 장소에 설치하면 안 되나요?",
    "세탁 및 건조할 수 없는 세탁물은?",
    "세제를 자동으로 넣을 수 있나요?",
    "가루세제는 자동 투입 장치에 넣을 수 있나요?",
    "어떤 상황에서 전원을 차단하고 서비스센터에 연락해야 하나요?",
    "건조 중 제품 문을 열면 어떻게 되나요?",
    "통세척 코스에 세제 넣어도 되나요?",
    "세탁 전 확인사항은 어떤 것이 있나요?"
]

API_URL = "http://0.0.0.0:8000/api/chat/manual"
DOC_NAME = "bespoke"
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY 
}

LOG_FILE = "results_log.txt"

# 새 로그 파일을 작성할 수 있도록 초기화
with open(LOG_FILE, "w", encoding="utf-8") as f:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"=== 시뮬레이션 시작: {now} ===\n\n")

def log_to_file(content: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n")

async def ask_question(session, question):
    payload = {
        "doc_name": DOC_NAME,
        "question": question
    }
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    try:
        response = await session.post(API_URL, json=payload, headers=HEADERS, timeout=60)
        latency = round(time.perf_counter() - start, 2)
        result = response.json()
        answer = result.get("answer", "").strip().replace("\n", " ")
        is_valid = bool(answer) and answer.lower() != "no answer"

        log_entry = (
            f"[{request_id}] {'✅' if is_valid else '❌'} time: {latency}s\n"
            f"Q: {question}\n"
            f"A: {answer if answer else 'No answer'}\n"
            "------------------------------"
        )
        log_to_file(log_entry)
        return latency if is_valid else None
    except Exception as e:
        error_entry = f"[{request_id}]  Error: {str(e)}"
        log_to_file(error_entry)
        return None

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [ask_question(client, q) for q in questions]
        latencies = await asyncio.gather(*tasks)
        valid = [l for l in latencies if l is not None]
        if valid:
            avg = round(sum(valid) / len(valid), 2)
            summary = f"\n 평균 응답 시간: {avg}초 (성공 {len(valid)} / {len(questions)}개)"
        else:
            summary = "\n 모든 요청 실패"
        log_to_file(summary)

if __name__ == "__main__":
    asyncio.run(main())
