import os

VLLM_API_URL = "http://localhost:8001/v1/completions"
LLM_MODEL_PATH = "rtzr/ko-gemma-2-9b-it"
EMBEDDING_MODEL_PATH = "nlpai-lab/KURE-v1"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project_root/
DATA_DIR = os.path.join(BASE_DIR, "data/raw")
CHROMA_DIR = os.path.join(BASE_DIR, "data/chroma_db")
