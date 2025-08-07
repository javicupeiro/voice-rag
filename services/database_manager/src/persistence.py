import sqlite3
import chromadb
from typing import List, Dict
import logging
import os
from .config import settings

# Get a logger for this module
logger = logging.getLogger(__name__)

# --- Repository for SQLite ---
class SQLiteRepository:
    def __init__(self, db_path: str = settings.SQLITE_DB_PATH):
        self.db_path = db_path
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_table()
        logger.info(f"SQLiteRepository initialized with a database at {self.db_path}")

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS original_chunks (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to create SQLite table: {e}")
            raise

    def save_chunk(self, chunk_id: str, content: str):
        logger.debug(f"Attempting to save chunk with id: {chunk_id}")
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO original_chunks (id, content) VALUES (?, ?)", (chunk_id, content))
                conn.commit()
            logger.info(f"Successfully saved chunk with id: {chunk_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to save chunk with id {chunk_id}: {e}")
            raise

    def get_chunks_by_ids(self, ids: List[str]) -> List[Dict]:
        logger.debug(f"Attempting to retrieve {len(ids)} chunks from SQLite.")
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                placeholders = ','.join('?' for _ in ids)
                query = f"SELECT id, content as original_chunk FROM original_chunks WHERE id IN ({placeholders})"
                cursor.execute(query, ids)
                results = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Retrieved {len(results)} out of {len(ids)} requested chunks.")
                return results
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve chunks by IDs: {e}")
            raise


# --- Repository for ChromaDB ---
class ChromaRepository:
    def __init__(self, path: str = settings.CHROMA_DB_PATH):
        self.path = path
        try:
            # Use a persistent client so data isn't lost on restart
            self.client = chromadb.PersistentClient(path=self.path)
            # Get or create the collection where embeddings will be stored
            self.collection = self.client.get_or_create_collection(name="pdf_summaries")
            logger.info(f"ChromaRepository initialized with a database at {self.path}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB at {self.path}: {e}")
            raise
        
    def save_embedding(self, chunk_id: str, embedding: List[float], metadata: Dict):
        logger.debug(f"Attempting to save embedding for chunk id: {chunk_id}")
        try:
            self.collection.add(
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[chunk_id]
            )
            logger.info(f"Successfully saved embedding for chunk id: {chunk_id}")
        except Exception as e:
            logger.error(f"Failed to save embedding for chunk id {chunk_id}: {e}")
            raise

    def query_embeddings(self, query_embedding: List[float], k: int) -> List[str]:
        logger.debug(f"Querying for {k} nearest neighbors.")
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            ids = results['ids'][0] if results and results['ids'] else []
            logger.info(f"Found {len(ids)} similar chunk(s) in ChromaDB.")
            return ids
        except Exception as e:
            logger.error(f"Failed to query embeddings: {e}")
            raise
