# services/database_manager/src/main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from . import schemas, domain_service, persistence, config
import logging

# The logger is configured in config.py, we just need to get it
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Database Service",
    description="Microservice to manage ChromaDB and SQLite for the RAG system.",
    version="1.0.0"
)


# Initialize the domain service (with its persistence dependencies)
# FastAPI will "inject" this dependency where needed
def get_domain_service():
    """Dependency Provider for the Domain Service."""
    try:
        return domain_service.DatabaseService(
            sqlite_repo=persistence.SQLiteRepository(),
            chroma_repo=persistence.ChromaRepository()
        )
    except Exception as e:
        logger.critical(f"Failed to initialize persistence layers: {e}", exc_info=True)
        # This will prevent the app from starting if DBs can't be initialized
        raise RuntimeError("Could not initialize database services.") from e

@app.post("/add-data", response_model=schemas.DataIngestionResponse, status_code=201)
def add_data(
    request: schemas.DataIngestionRequest,
    service: domain_service.DatabaseService = Depends(get_domain_service)
):
    """
    Endpoint to add a new chunk along with its summary/embedding.
    1. Stores the original chunk in SQLite.
    2. Stores the embedding and the summary in ChromaDB.
    """
    try:
        stored_id = service.add_data(
            chunk_id=request.chunk_id,
            original_chunk=request.original_chunk,
            summary_chunk=request.summary_chunk,
            embedding=request.embedding
        )
        logger.info(f"Successfully processed add-data request for chunk_id: {stored_id}")
        return {"status": "success", "stored_id": stored_id}
    except Exception as e:
        logger.error(f"An error occurred while adding data for chunk_id {request.chunk_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while saving data.")


@app.post("/retrieve-chunks", response_model=schemas.QueryResponse)
def retrieve_chunks(
    request: schemas.QueryRequest,
    service: domain_service.DatabaseService = Depends(get_domain_service)
):
    """
    Endpoint to search for chunks relevant to a query.
    1. Queries ChromaDB for the most similar chunk IDs.
    2. Uses those IDs to retrieve the original chunks from SQLite.
    """
    logger.info(f"Received request to retrieve {request.k} chunks.")
    try:
        chunks = service.retrieve_relevant_chunks(
            query_embedding=request.query_embedding,
            k=request.k
        )
        logger.info(f"Successfully processed retrieve-chunks request, found {len(chunks)} chunk(s).")
        return {"retrieved_chunks": chunks}
    except Exception as e:
        logger.error(f"An error occurred while retrieving chunks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred while retrieving data.")
