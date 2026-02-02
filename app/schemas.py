from pydantic import BaseModel

class AskQuestion(BaseModel):
    document_id: str
    question: str

class Answer(BaseModel):
    answer: str

class Upload(BaseModel):
    id: str       
    filename: str
    message: str