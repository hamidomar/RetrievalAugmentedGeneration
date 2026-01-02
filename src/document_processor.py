import os
from typing import List, Dict, Any
import hashlib
from datetime import datetime
from pathlib import Path
import pypdf
import docx
from bs4 import BeautifulSoup

class DocumentProcessor:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process a file and return a list of chunks with metadata.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_ext = file_path.suffix.lower()
        content = ""
        
        try:
            if file_ext == '.pdf':
                content = self._read_pdf(file_path)
            elif file_ext == '.docx':
                content = self._read_docx(file_path)
            elif file_ext in ['.txt', '.md']:
                content = self._read_text(file_path)
            elif file_ext == '.html':
                content = self._read_html(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            return self._chunk_content(content, file_path.name)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []

    def _read_pdf(self, path: Path) -> str:
        text = ""
        with open(path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
        return text

    def _read_docx(self, path: Path) -> str:
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _read_text(self, path: Path) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _read_html(self, path: Path) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            return soup.get_text(separator='\n')

    def _chunk_content(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """
        Split content into chunks with overlap.
        """
        # Simple token estimation (approx 4 chars per token)
        # For production, use tiktoken, but simple split is okay for now or we can use tiktoken if installed.
        
        # Let's use a simple character-based splitter for robustness first, 
        # but since we have tiktoken in requirements, let's use it for better accuracy.
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(content)
        
        chunks = []
        total_tokens = len(tokens)
        
        start = 0
        chunk_index = 0
        
        while start < total_tokens:
            end = min(start + self.chunk_size, total_tokens)
            chunk_tokens = tokens[start:end]
            chunk_text = enc.decode(chunk_tokens)
            
            # Create chunk ID
            chunk_id = hashlib.md5(f"{filename}_{chunk_index}".encode()).hexdigest()
            
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "metadata": {
                    "source": filename,
                    "chunk_index": chunk_index,
                    "processed_date": datetime.now().isoformat(),
                    "token_count": len(chunk_tokens)
                }
            })
            
            if end == total_tokens:
                break
                
            start += (self.chunk_size - self.chunk_overlap)
            chunk_index += 1
            
        return chunks
