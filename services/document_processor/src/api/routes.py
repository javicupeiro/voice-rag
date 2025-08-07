from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile

from services.parser import PdfParser
from models.chunk import DocumentChunkOut

router = APIRouter()

@router.post("/process-pdf/", response_model=list[DocumentChunkOut])
async def process_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")

    # Guardar el archivo temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    # Procesar el PDF
    parser = PdfParser()
    chunks = parser.parse(tmp_path)

    # Convertimos los DocumentChunk a Pydantic para respuesta JSON
    return [DocumentChunkOut.model_validate(chunk.__dict__) for chunk in chunks]