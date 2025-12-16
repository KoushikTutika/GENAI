import requests
from bs4 import BeautifulSoup
import os
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer

class WebCrawler:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection("tata_docs")
        
    def crawl_html_pages(self) -> List[Dict]:
        pages = [
            "index.html", "passenger-cars.html", "commercial-vehicles.html",
            "electric-vehicles.html", "sales-offers.html", "brochures.html",
            "contact.html", "nexon-brochure.html", "harrier-brochure.html",
            "nexon-ev-brochure.html"
        ]
        
        documents = []
        for page in pages:
            try:
                # Read local HTML files
                file_path = f"Sample_Html_Car_Sales/{page}"
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text(strip=True)
                    
                    doc = {
                        "id": page.replace('.html', ''),
                        "url": f"{self.base_url}/{page}",
                        "title": soup.find('title').text if soup.find('title') else page,
                        "content": text,
                        "page_type": self._get_page_type(page)
                    }
                    documents.append(doc)
                    
            except Exception as e:
                print(f"Error crawling {page}: {e}")
                
        return documents
    
    def _get_page_type(self, page: str) -> str:
        if "brochure" in page:
            return "brochure"
        elif "passenger" in page:
            return "passenger_cars"
        elif "commercial" in page:
            return "commercial_vehicles"
        elif "electric" in page:
            return "electric_vehicles"
        elif "sales" in page:
            return "sales_offers"
        elif "contact" in page:
            return "contact"
        else:
            return "general"
    
    def store_documents(self, documents: List[Dict]):
        for doc in documents:
            # Split content into chunks
            chunks = self._chunk_text(doc['content'])
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc['id']}_chunk_{i}"
                embedding = self.model.encode(chunk).tolist()
                
                self.collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        "page_id": doc['id'],
                        "url": doc['url'],
                        "title": doc['title'],
                        "page_type": doc['page_type'],
                        "chunk_index": i
                    }],
                    ids=[chunk_id]
                )
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict]:
        query_embedding = self.model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return [{
            "content": doc,
            "metadata": meta,
            "distance": dist
        } for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )]