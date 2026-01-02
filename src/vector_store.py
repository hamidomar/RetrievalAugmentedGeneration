import os
import json
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import Json
from openai import OpenAI
import numpy as np

class VectorStore:
    def __init__(self, connection_string: str):
        self.conn_str = connection_string
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._init_db()

    def _get_conn(self):
        return psycopg2.connect(self.conn_str)

    def _init_db(self):
        """Initialize the database with vector extension and table."""
        try:
            with self._get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS documents (
                            id TEXT PRIMARY KEY,
                            content TEXT,
                            metadata JSONB,
                            embedding vector(3072)
                        );
                    """)
                    # Create index for faster retrieval
                    # ivfflat is good for recall/speed balance, but requires some data to build effectively.
                    # For simplicity and smaller datasets, exact search or HNSW (if available in newer pgvector) is fine.
                    # Let's stick to basic table for now, add index later if needed.
                conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        text = text.replace("\n", " ")
        return self.client.embeddings.create(input=[text], model="text-embedding-3-large").data[0].embedding

    def add_documents(self, chunks: List[Dict[str, Any]]):
        """Add chunks to the vector store."""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                for chunk in chunks:
                    embedding = self.get_embedding(chunk['text'])
                    cur.execute("""
                        INSERT INTO documents (id, content, metadata, embedding)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE 
                        SET content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding;
                    """, (
                        chunk['id'],
                        chunk['text'],
                        Json(chunk['metadata']),
                        embedding
                    ))
            conn.commit()

    def delete_document(self, filename: str):
        """Delete all chunks belonging to a specific file."""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM documents WHERE metadata->>'source' = %s", (filename,))
            conn.commit()

    def query(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find most similar chunks."""
        query_embedding = self.get_embedding(query_text)
        
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, content, metadata, 1 - (embedding <=> %s::vector) as similarity
                    FROM documents
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                """, (query_embedding, query_embedding, limit))
                
                results = []
                for row in cur.fetchall():
                    results.append({
                        "id": row[0],
                        "text": row[1],
                        "metadata": row[2],
                        "score": row[3]
                    })
                return results

    def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[Dict[str, Any]]:
        """Retrieve specific chunks by ID (used for adjacency)."""
        if not chunk_ids:
            return []
            
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, content, metadata
                    FROM documents
                    WHERE id = ANY(%s);
                """, (chunk_ids,))
                
                results = []
                for row in cur.fetchall():
                    results.append({
                        "id": row[0],
                        "text": row[1],
                        "metadata": row[2]
                    })
                return results
    
    def get_all_documents(self) -> List[str]:
        """Get list of all indexed filenames."""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT metadata->>'source' FROM documents;")
                return [row[0] for row in cur.fetchall()]
