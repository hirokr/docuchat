from fastapi import APIRouter, UploadFile, File
router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # TODO: parse PDF → chunk → embed → upsert to Pinecone
    return {"filename": file.filename, "status": "queued"}
