import asyncio
import httpx
import time
import uuid
from datetime import datetime

questions = [
    "비스포크 제트 청소기의 충전 시간은 얼마나 걸리나요?",
    "비스포크 제트 청소기의 먼지통은 어떻게 비우나요?",
    "비스포크 청소기의 헤파 필터는 물세척이 가능한가요?",
    "충전대에 청소기를 거치하면 자동으로 충전되나요?",
    "배터리 탈착은 어떻게 하나요?",
    "비스포크 제트 청소기의 흡입력은 몇 단계인가요?",
    "디스플레이에서 확인할 수 있는 정보는 어떤 것이 있나요?",
    "비스포크 청소기의 먼지통 세척 주기는 어떻게 되나요?",
    "청소기 사용 중 필터 교체 알림이 뜨면 어떻게 해야 하나요?",
    "비스포크 제트 청소기를 장기간 보관할 때 주의사항은 무엇인가요?"
]

API_URL = "http://0.0.0.0:8000/api/chat/manual"  # 👈 실제 주소로 바꾸세요
DOC_NAME = "bespoke"
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": "AKIA2HSMPZTDHD5NQQK5"  # 필요시
}

LOG_FILE = "results_log.txt"

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
        answer = result.get("answer", "No answer")[:200].replace("\n", " ")
        log_entry = (
            f"[{request_id}] ⏱️ {latency}s\n"
            f"Q: {question}\n"
            f"A: {answer}\n"
            "------------------------------"
        )
        print(log_entry)
        log_to_file(log_entry)
        return latency
    except Exception as e:
        error_entry = f"[{request_id}] ❌ Error: {str(e)}"
        print(error_entry)
        log_to_file(error_entry)
        return None

async def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_to_file(f"\n=== 시뮬레이션 시작: {now} ===\n")
    async with httpx.AsyncClient() as client:
        tasks = [ask_question(client, q) for q in questions]
        latencies = await asyncio.gather(*tasks)
        valid = [l for l in latencies if l is not None]
        if valid:
            avg = round(sum(valid) / len(valid), 2)
            summary = f"\n📊 평균 응답 시간: {avg}초 (성공 {len(valid)} / {len(questions)}개)"
        else:
            summary = "❌ 모든 요청 실패"
        print(summary)
        log_to_file(summary)

if __name__ == "__main__":
    asyncio.run(main())
