import os
import json
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class SimpleRAGAgent:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = None
        self.index = None
        
    def scrape_html_files(self, html_dir):
        """Scrape content from HTML files in directory"""
        for filename in os.listdir(html_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(html_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text and split into chunks
                    text = soup.get_text(separator=' ', strip=True)
                    title = soup.title.string if soup.title else filename
                    
                    # Split into paragraphs
                    chunks = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
                    
                    for chunk in chunks:
                        self.documents.append({
                            'text': chunk,
                            'source': filename,
                            'title': title
                        })
        
        print(f"Scraped {len(self.documents)} chunks from {html_dir}")
    
    def build_index(self):
        """Build FAISS index from documents"""
        if not self.documents:
            print("No documents to index!")
            return
        
        texts = [doc['text'] for doc in self.documents]
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
        
        print(f"Built index with {len(self.documents)} documents")
    
    def ask(self, question, top_k=3):
        """Answer question using RAG"""
        if self.index is None:
            return "Index not built. Please scrape and build index first."
        
        # Encode question
        question_embedding = self.model.encode([question])
        
        # Search index
        distances, indices = self.index.search(question_embedding.astype('float32'), top_k)
        
        # Get relevant documents
        results = []
        for idx in indices[0]:
            results.append(self.documents[idx])
        
        # Format answer
        answer = f"\n{'='*60}\nQuestion: {question}\n{'='*60}\n\n"
        answer += "Top relevant passages:\n\n"
        
        for i, doc in enumerate(results, 1):
            answer += f"{i}. [{doc['source']}]\n{doc['text'][:300]}...\n\n"
        
        return answer

if __name__ == "__main__":
    agent = SimpleRAGAgent()
    
    # Scrape HTML files from car-sales-webapp
    html_dir = "../car-sales-webapp/src/main/resources/static"
    agent.scrape_html_files(html_dir)
    
    # Build index
    agent.build_index()
    
    # Interactive Q&A
    print("\n" + "="*60)
    print("RAG Agent Ready! Ask questions (type 'quit' to exit)")
    print("="*60 + "\n")
    
    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
        if question:
            print(agent.ask(question))
