"""Text processing and chunking utilities"""

import re
from typing import List, Dict
from .config import config

class TextProcessor:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or config.chunk_size
        self.chunk_overlap = chunk_overlap or config.chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', ' ', text)
        return text.strip()
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk_data = {
                'text': chunk_text,
                'chunk_id': len(chunks),
                'start_word': i,
                'end_word': min(i + self.chunk_size, len(words))
            }
            
            # Add metadata if provided
            if metadata:
                chunk_data.update(metadata)
            
            chunks.append(chunk_data)
            
            # Break if we've covered all words
            if i + self.chunk_size >= len(words):
                break
        
        return chunks
    
    def process_documents(self, documents: List[Dict]) -> List[Dict]:
        """Process multiple documents into chunks"""
        all_chunks = []
        
        for doc_idx, doc in enumerate(documents):
            clean_content = self.clean_text(doc['content'])
            
            metadata = {
                'doc_id': doc_idx,
                'url': doc['url'],
                'title': doc['title'],
                'doc_length': doc['length']
            }
            
            chunks = self.chunk_text(clean_content, metadata)
            all_chunks.extend(chunks)
        
        return all_chunks