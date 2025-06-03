from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dependencies import get_dependencies
from schemas import QuestionRequest
from services import *
from utils import verify_api_key

router = APIRouter()

@router.get("/")
def home(api_key: str = Depends(verify_api_key)):
    return {"message": "Hello, World!"}

@router.post("/api/manuals/upload")
async def upload_pdf(doc_name: str = Form(...), file: UploadFile = File(...), dependencies: dict = Depends(get_dependencies), api_key: str = Depends(verify_api_key)):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed"})
    
    try:
        await asyncio.to_thread(
            process_pdf,
            doc_name,
            file,
            dependencies["chroma_client"],
            dependencies["sentence_model"]
        )

        return JSONResponse(
            status_code=200,  # 또는 201
            content={"message": "PDF uploaded successfully", "doc_name": doc_name}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/api/chat/manual")
async def ask(request: QuestionRequest, dependencies: dict = Depends(get_dependencies), api_key: str = Depends(verify_api_key)):
    try:
        answer, img_lst = await get_llm_answer(
            request,
            dependencies["chroma_client"],
            dependencies["model_manager"]
        )

        return JSONResponse(
            status_code=200,  # 또는 201
            content={"message": "LLM responded successfully", "answer": answer, "images": img_lst}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


    