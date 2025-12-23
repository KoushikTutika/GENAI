"""RAG (Retrieval-Augmented Generation) pipeline"""

import os
from typing import List, Dict, Tuple, Optional
from collections import Counter
import re
from .index import VectorIndex
from .config import config

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class RAGPipeline:
    def __init__(self, index_dir: str, model: str = None):
        self.index = VectorIndex()
        self.index.load(index_dir)
        self.model = model or config.default_model
        
        # Initialize OpenAI client if available and configured
        self.openai_client = None
        if OPENAI_AVAILABLE and config.openai_api_key:
            self.openai_client = OpenAI(api_key=config.openai_api_key)
    
    def retrieve(self, query: str, top_k: int = None, use_mmr: bool = True) -> List[Tuple[Dict, float]]:
        """Retrieve relevant chunks"""
        if use_mmr:
            return self.index.mmr_search(query, top_k)
        else:
            return self.index.search(query, top_k)
    
    def generate_extractive_answer(self, query: str, results: List[Tuple[Dict, float]]) -> Dict:
        """Generate extractive answer without LLM"""
        if not results:
            return {
                'answer': "No relevant information found.",
                'sources': [],
                'passages': []
            }
        
        # Extract passages and sources
        passages = []
        sources = set()
        
        for chunk, score in results:
            passages.append({
                'text': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text'],
                'score': score,
                'source': chunk['title'],
                'url': chunk['url']
            })
            sources.add((chunk['title'], chunk['url']))
        
        # Generate simple extractive answer
        top_passage = results[0][0]['text']
        answer = top_passage[:300] + "..." if len(top_passage) > 300 else top_passage
        
        return {
            'answer': answer,
            'sources': list(sources),
            'passages': passages
        }
    
    def generate_llm_answer(self, query: str, results: List[Tuple[Dict, float]]) -> Dict:
        """Generate answer using OpenAI LLM"""
        if not self.openai_client:
            return self.generate_extractive_answer(query, results)
        
        if not results:
            return {
                'answer': "No relevant information found.",
                'sources': [],
                'passages': []
            }
        
        # Prepare context from retrieved chunks
        context_parts = []
        sources = set()
        
        for i, (chunk, score) in enumerate(results):
            context_parts.append(f"[{i+1}] {chunk['text']}")
            sources.add((chunk['title'], chunk['url']))
        
        context = "\n\n".join(context_parts)
        
        # Create prompt
        prompt = f"""Based on the following context, answer the question. Include citations using [1], [2], etc. format.

Context:
{context}

Question: {query}

Answer:"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Always include citations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Extract passages for display
            passages = []
            for chunk, score in results:
                passages.append({
                    'text': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text'],
                    'score': score,
                    'source': chunk['title'],
                    'url': chunk['url']
                })
            
            return {
                'answer': answer,
                'sources': list(sources),
                'passages': passages
            }
            
        except Exception as e:
            print(f"Error generating LLM answer: {e}")
            return self.generate_extractive_answer(query, results)
    
    def ask(self, query: str, use_llm: bool = None, top_k: int = None) -> Dict:
        """Main query interface"""
        # Determine if we should use LLM
        if use_llm is None:
            use_llm = self.openai_client is not None
        
        # Retrieve relevant chunks
        results = self.retrieve(query, top_k)
        
        # Generate answer
        if use_llm:
            response = self.generate_llm_answer(query, results)
        else:
            response = self.generate_extractive_answer(query, results)
        
        # Add insights
        response['insights'] = self.generate_insights(results)
        
        return response
    
    def generate_insights(self, results: List[Tuple[Dict, float]]) -> Dict:
        """Generate insights from retrieved results"""
        if not results:
            return {'common_terms': [], 'sources_count': 0}
        
        # Extract common terms
        all_text = " ".join([chunk['text'] for chunk, _ in results])
        words = re.findall(r'\b\w+\b', all_text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        filtered_words = [word for word in words if len(word) > 3 and word not in stop_words]
        
        common_terms = Counter(filtered_words).most_common(10)
        
        # Count unique sources
        sources = set(chunk['url'] for chunk, _ in results)
        
        return {
            'common_terms': common_terms,
            'sources_count': len(sources)
        }