from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from app.database import get_db, Document
from app.ocr import extract_text
from app.llm import ask_llm
from app.schemas import AskQuestion, Answer, Upload
import hashlib
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=Upload)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    try:
        content = await file.read()
        file_hash = hashlib.md5(content).hexdigest()
        cur_doc = db.query(Document).filter(Document.id == file_hash).first()
        
        if cur_doc:
            return {
                "id": cur_doc.id, 
                "filename": cur_doc.filename, 
                "message": "Document already exists"
            }
        
        extracted_text = await run_in_threadpool(extract_text, content)
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text detected.")
        
        new_doc = Document(id=file_hash, filename=file.filename, extracted_text=extracted_text)
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        return {"id": new_doc.id, "filename": new_doc.filename, "message": "Processed successfully"}

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask", response_model=Answer)
async def ask_question(request: AskQuestion, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == request.document_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    answer = await ask_llm(doc.extracted_text, request.question)
    return {"answer": answer}