"""FAISS vector index management"""

import os
import json
import faiss
import numpy as np
from typing import List, Dict, Tuple
from .embeddings import EmbeddingModel
from .processing import TextProcessor
from .config import config

class VectorIndex:
    def __init__(self, embedding_model: EmbeddingModel = None):
        self.embedding_model = embedding_model or EmbeddingModel()
        self.index = None
        self.metadata = []
    
    def build_index(self, chunks: List[Dict]) -> None:
        """Build FAISS index from text chunks"""
        if not chunks:
            raise ValueError("No chunks provided")
        
        # Extract texts for embedding
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype(np.float32))
        
        # Store metadata
        self.metadata = chunks
        
        print(f"Built index with {len(chunks)} chunks, dimension {dimension}")
    
    def save(self, index_dir: str) -> None:
        """Save index and metadata to disk"""
        os.makedirs(index_dir, exist_ok=True)
        
        # Save FAISS index
        index_path = os.path.join(index_dir, "index.faiss")
        faiss.write_index(self.index, index_path)
        
        # Save metadata
        metadata_path = os.path.join(index_dir, "metadata.jsonl")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            for item in self.metadata:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"Saved index to {index_dir}")
    
    def load(self, index_dir: str) -> None:
        """Load index and metadata from disk"""
        # Load FAISS index
        index_path = os.path.join(index_dir, "index.faiss")
        self.index = faiss.read_index(index_path)
        
        # Load metadata
        metadata_path = os.path.join(index_dir, "metadata.jsonl")
        self.metadata = []
        with open(metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.metadata.append(json.loads(line.strip()))
        
        print(f"Loaded index from {index_dir} with {len(self.metadata)} chunks")
    
    def search(self, query: str, top_k: int = None) -> List[Tuple[Dict, float]]:
        """Search the index for similar chunks"""
        if not self.index:
            raise ValueError("Index not built or loaded")
        
        top_k = top_k or config.top_k
        
        # Encode query
        query_embedding = self.embedding_model.encode_single(query)
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Return results with metadata
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(score)))
        
        return results
    
    def mmr_search(self, query: str, top_k: int = None, diversity: float = None) -> List[Tuple[Dict, float]]:
        """Search with Maximal Marginal Relevance for diversity"""
        top_k = top_k or config.top_k
        diversity = diversity or config.mmr_diversity
        
        # Get more candidates than needed
        candidates = self.search(query, top_k * 3)
        if not candidates:
            return []
        
        # MMR selection
        selected = [candidates[0]]  # Start with most relevant
        candidates = candidates[1:]
        
        query_embedding = self.embedding_model.encode_single(query)
        
        while len(selected) < top_k and candidates:
            best_score = -float('inf')
            best_idx = 0
            
            for i, (candidate, _) in enumerate(candidates):
                # Relevance score
                candidate_embedding = self.embedding_model.encode_single(candidate['text'])
                relevance = np.dot(query_embedding, candidate_embedding)
                
                # Diversity score (minimum similarity to selected items)
                diversity_score = float('inf')
                for selected_item, _ in selected:
                    selected_embedding = self.embedding_model.encode_single(selected_item['text'])
                    similarity = np.dot(candidate_embedding, selected_embedding)
                    diversity_score = min(diversity_score, similarity)
                
                # MMR score
                mmr_score = diversity * relevance - (1 - diversity) * diversity_score
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i
            
            selected.append(candidates.pop(best_idx))
        
        return selected

def build_index_from_docstore(docstore_path: str, index_dir: str) -> VectorIndex:
    """Build index from a docstore file"""
    from .scrape import load_docstore
    
    # Load documents
    documents = load_docstore(docstore_path)
    
    # Process into chunks
    processor = TextProcessor()
    chunks = processor.process_documents(documents)
    
    # Build index
    index = VectorIndex()
    index.build_index(chunks)
    index.save(index_dir)
    
    return index