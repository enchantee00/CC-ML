import torch
import httpx

from vllm import LLM, SamplingParams
from sentence_transformers import SentenceTransformer


from config import VLLM_API_URL, LLM_MODEL_PATH, EMBEDDING_MODEL_PATH

class ModelManager:
    def __init__(self):
        self.llm = None
        self.sentence_model = None
        
        self._load_model()
        

    def _load_model(self):
        device = torch.device("cuda:3")
        self.sentence_model = SentenceTransformer(EMBEDDING_MODEL_PATH, device=device)


async def generate_response(prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    payload = {
        "model": LLM_MODEL_PATH,  # 필요 시 config로 분리
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(VLLM_API_URL, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["text"].strip()
    