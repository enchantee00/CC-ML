from pydantic import BaseModel

class QuestionRequest(BaseModel):
    doc_name: str
    question: str

class DocNameRequest(BaseModel):
    doc_name: str