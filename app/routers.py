from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dependencies import get_dependencies
from schemas import QuestionRequest
from services import *

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Hello, World!"}

@router.post("/documents")
async def upload_pdf(doc_name: str = Form(...), file: UploadFile = File(...), dependencies: dict = Depends(get_dependencies)):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed"})
    
    process_pdf(doc_name, file, dependencies["chroma_client"], dependencies["model_manager"])

    return JSONResponse(
        status_code=200,  # 또는 201
        content={"message": "PDF uploaded successfully", "filename": file.filename}
    )


@router.post("/ask")
async def ask(request: QuestionRequest, dependencies: dict = Depends(get_dependencies)):
    answer, img_lst = await get_llm_answer(
        request,
        dependencies["chroma_client"],
        dependencies["model_manager"]
    )

    return JSONResponse(
        status_code=200,  # 또는 201
        content={"message": "LLM responded successfully", "answer": answer, "images": img_lst}
    )


    