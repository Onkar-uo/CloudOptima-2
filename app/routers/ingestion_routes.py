from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.csv_store import InMemoryCSVStore

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])
store = InMemoryCSVStore()

class IngestFileRequest(BaseModel):
    file_path: str

@router.get("/files")
def list_files():
    return store.list_files()

@router.post("/process-single")
def load_single_csv(payload: IngestFileRequest):
    try:
        return store.load_single_file(payload.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-db")
def reset_store():
    return store.clear()