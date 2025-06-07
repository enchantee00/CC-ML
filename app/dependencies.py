from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import chromadb

from inference import ModelManager
from config import CHROMA_DIR

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@asynccontextmanager
async def lifespan(app: FastAPI):    
    model_manager = ModelManager()
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    app.state.model_manager = model_manager
    app.state.chroma_client = client

    yield  # 애플리케이션 실행

    del model_manager
    print("서버 종료: 모델 리소스 해제")


def get_dependencies(request: Request):
    return {
        "model_manager": request.app.state.model_manager,
        "chroma_client": request.app.state.chroma_client
    }