import os

LLM_MODEL_PATH = "rtzr/ko-gemma-2-9b-it"
EMBEDDING_MODEL_PATH = "nlpai-lab/KURE-v1"

CHROMA_DB_PATH = "../data/chroma_db"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project_root/
DATA_DIR = os.path.join(BASE_DIR, "data")
