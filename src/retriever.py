import hashlib
from typing import List, Dict, Any, Set
from vector_store import VectorStore

class Retriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def _generate_chunk_id(self, filename: str, index: int) -> str:
        return hashlib.md5(f"{filename}_{index}".encode()).hexdigest()

    def retrieve(self, query: str, top_k: int = 5, adjacency_window: int = 1) -> Dict[str, Any]:
        """
        Retrieve chunks and their context.
        Returns a dict with 'primary_chunks' and 'context_chunks'.
        """
        # 1. Get primary chunks
        primary_chunks = self.vector_store.query(query, limit=top_k)
        
        # 2. Identify adjacent IDs
        adjacent_ids: Set[str] = set()
        
        for chunk in primary_chunks:
            filename = chunk['metadata']['source']
            current_index = chunk['metadata']['chunk_index']
            
            # Look before and after
            for i in range(1, adjacency_window + 1):
                prev_index = current_index - i
                next_index = current_index + i
                
                if prev_index >= 0:
                    adjacent_ids.add(self._generate_chunk_id(filename, prev_index))
                
                # We don't know the max index easily, but querying a non-existent ID just returns nothing, which is fine.
                adjacent_ids.add(self._generate_chunk_id(filename, next_index))
        
        # Filter out IDs that are already in primary chunks to avoid duplicates in fetching
        primary_ids = {c['id'] for c in primary_chunks}
        ids_to_fetch = list(adjacent_ids - primary_ids)
        
        # 3. Fetch adjacent chunks
        context_chunks = self.vector_store.get_chunks_by_ids(ids_to_fetch)
        
        # Map context chunks by ID for easy lookup
        context_map = {c['id']: c for c in context_chunks}
        
        # 4. Structure the result
        # We want to attach context to the primary chunks if possible, or just return them as a pool.
        # Let's return a structured response where each primary chunk has its specific context attached,
        # but also provide a flat list for the LLM.
        
        expanded_results = []
        
        for chunk in primary_chunks:
            filename = chunk['metadata']['source']
            current_index = chunk['metadata']['chunk_index']
            
            chunk_context = {
                "before": [],
                "after": []
            }
            
            # Find specific context for this chunk
            for i in range(1, adjacency_window + 1):
                prev_id = self._generate_chunk_id(filename, current_index - i)
                next_id = self._generate_chunk_id(filename, current_index + i)
                
                if prev_id in context_map:
                    chunk_context["before"].append(context_map[prev_id])
                if next_id in context_map:
                    chunk_context["after"].append(context_map[next_id])
            
            # Sort context by index to ensure order
            chunk_context["before"].sort(key=lambda x: x['metadata']['chunk_index'])
            chunk_context["after"].sort(key=lambda x: x['metadata']['chunk_index'])
            
            expanded_results.append({
                "primary": chunk,
                "context": chunk_context
            })
            
        return expanded_results
