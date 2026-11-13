from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.resume import UserResume
from app.services.parser import extract_text, parse_resume

router = APIRouter(prefix="/api/v1/resume", tags=["Resume"])

@router.post("/parse")
async def parse(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(400, "Only .pdf and .docx files allowed")
    data = await file.read()
    try:
        text = extract_text(file.filename, data)
    except Exception:
        raise HTTPException(400, "Could not read the file")
    result = parse_resume(text)
    
    row = UserResume(filename=file.filename, extracted_json=result)
    db.add(row)
    await db.commit()
    return {**result, "resume_id": row.id}