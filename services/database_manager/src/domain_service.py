from .persistence import SQLiteRepository, ChromaRepository
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, sqlite_repo: SQLiteRepository, chroma_repo: ChromaRepository):
        """Initializes the service with persistence layer dependencies."""
        # Dependency injection: The service receives the DB connections
        self.sqlite_repo = sqlite_repo
        self.chroma_repo = chroma_repo
        logger.info("DatabaseService initialized.")

    def add_data(self, chunk_id: str, original_chunk: str, summary_chunk: str, embedding: List[float]) -> str:
        """
        Orchestrates saving chunk data to its respective databases.
        """
        logger.info(f"Orchestrating data addition for chunk_id: {chunk_id}")
        
        # 1. Save the original chunk content
        logger.debug("Calling SQLiteRepository to save original chunk.")
        self.sqlite_repo.save_chunk(chunk_id, original_chunk)
        
        # 2. Save the embedding and summary
        logger.debug("Calling ChromaRepository to save embedding and summary.")
        self.chroma_repo.save_embedding(
            chunk_id=chunk_id,
            embedding=embedding,
            metadata={"summary": summary_chunk}
        )
        
        logger.info(f"Successfully added all data for chunk_id: {chunk_id}")
        return chunk_id

    def retrieve_relevant_chunks(self, query_embedding: List[float], k: int) -> List[Dict]:
        """
        Orchestrates the retrieval of relevant chunks based on a query embedding.
        """
        logger.info(f"Orchestrating chunk retrieval for a query with k={k}")
        
        # 1. Get similar chunk IDs from the vector database
        logger.debug("Calling ChromaRepository to find similar chunks.")
        similar_ids = self.chroma_repo.query_embeddings(query_embedding, k)
        
        if not similar_ids:
            logger.warning("No similar chunks found in ChromaDB for the given query.")
            return []
            
        # 2. Retrieve the original chunk content for those IDs
        logger.debug(f"Calling SQLiteRepository to retrieve original content for {len(similar_ids)} IDs.")
        original_chunks = self.sqlite_repo.get_chunks_by_ids(similar_ids)
        
        logger.info(f"Successfully retrieved relevant chunks for the query.")
        return original_chunks
