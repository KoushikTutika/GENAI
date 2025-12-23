from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

app = Flask(__name__)

class WebRAGAgent:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = None
        self.index = None
        self.scraped_urls = []
        
    def scrape_url(self, url):
        """Scrape content from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            title = soup.title.string if soup.title else url
            
            # Split into chunks
            chunks = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
            
            for chunk in chunks:
                self.documents.append({
                    'text': chunk,
                    'source': url,
                    'title': title
                })
            
            self.scraped_urls.append(url)
            return True, f"Scraped {len(chunks)} chunks from {url}"
        except Exception as e:
            return False, f"Error scraping {url}: {str(e)}"
    
    def build_index(self):
        """Build FAISS index from documents"""
        if not self.documents:
            return False, "No documents to index!"
        
        texts = [doc['text'] for doc in self.documents]
        self.embeddings = self.model.encode(texts)
        
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
        
        return True, f"Built index with {len(self.documents)} documents"
    
    def ask(self, question, top_k=3):
        """Answer question using RAG"""
        if self.index is None:
            return []
        
        question_embedding = self.model.encode([question])
        distances, indices = self.index.search(question_embedding.astype('float32'), top_k)
        
        results = []
        for idx in indices[0]:
            results.append({
                'text': self.documents[idx]['text'][:500],
                'source': self.documents[idx]['source'],
                'title': self.documents[idx]['title']
            })
        
        return results

# Initialize agent
agent = WebRAGAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'success': False, 'message': 'URL is required'})
    
    success, message = agent.scrape_url(url)
    
    if success:
        agent.build_index()
    
    return jsonify({
        'success': success,
        'message': message,
        'total_docs': len(agent.documents),
        'scraped_urls': agent.scraped_urls
    })

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'success': False, 'message': 'Question is required'})
    
    if not agent.documents:
        return jsonify({'success': False, 'message': 'Please scrape a URL first'})
    
    results = agent.ask(question)
    
    return jsonify({
        'success': True,
        'results': results
    })

@app.route('/reset', methods=['POST'])
def reset():
    agent.documents = []
    agent.embeddings = None
    agent.index = None
    agent.scraped_urls = []
    return jsonify({'success': True, 'message': 'Agent reset successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
