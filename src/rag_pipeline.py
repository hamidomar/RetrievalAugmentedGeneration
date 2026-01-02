import os
from typing import List, Dict, Any
from openai import OpenAI
from retriever import Retriever

class RAGPipeline:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def answer_query(self, query: str) -> Dict[str, Any]:
        """
        End-to-end RAG pipeline.
        """
        # 1. Retrieve
        retrieval_results = self.retriever.retrieve(query)
        
        # 2. Format Context
        context_text = self._format_context(retrieval_results)
        
        # 3. Generate Answer
        system_prompt = """You are a helpful assistant for a RAG system. 
Use the provided context to answer the user's question. 
If the answer is not in the context, say you don't know.
Cite your sources using the format [Source: filename].
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        return {
            "answer": answer,
            "retrieval_details": retrieval_results
        }

    def _format_context(self, results: List[Dict[str, Any]]) -> str:
        formatted = []
        
        for item in results:
            primary = item['primary']
            context = item['context']
            
            # Construct a block: [Before] -> [Primary] -> [After]
            block = []
            
            for ctx in context['before']:
                block.append(f"(... {ctx['text']} ...)")
                
            block.append(f"TARGET CHUNK: {primary['text']}")
            
            for ctx in context['after']:
                block.append(f"(... {ctx['text']} ...)")
            
            source = primary['metadata']['source']
            score = primary.get('score', 0)
            
            formatted.append(f"--- Document: {source} (Relevance: {score:.4f}) ---\n" + "\n".join(block))
            
        return "\n\n".join(formatted)
