import torch

from vllm import LLM, SamplingParams
from sentence_transformers import SentenceTransformer


from config import LLM_MODEL_PATH, EMBEDDING_MODEL_PATH

class ModelManager:
    def __init__(self):
        self.llm = None
        self.sampling_params = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=512)
        self.sentence_model = None
        
        self._load_model()
        

    def _load_model(self):
        # vLLM 초기화
        self.llm = LLM(model=LLM_MODEL_PATH, tensor_parallel_size=2, gpu_memory_utilization=0.8, max_model_len=1024)

        device = torch.device("cuda:3")  # 원하는 GPU 번호로 설정
        self.sentence_model = SentenceTransformer(EMBEDDING_MODEL_PATH, device=device)


    def generate_response(self, prompt):
        # outputs = await asyncio.to_thread(llm.generate, [prompt], sampling_params)
        outputs = self.llm.generate([prompt], self.sampling_params)
        response = outputs[0].outputs[0].text.strip()
        return response
    
    