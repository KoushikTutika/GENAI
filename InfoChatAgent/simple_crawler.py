import os
from bs4 import BeautifulSoup
from typing import List, Dict
import json

class SimpleCrawler:
    def __init__(self):
        self.documents = []
        
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
                file_path = f"Sample_Html_Car_Sales/{page}"
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text(strip=True)
                    
                    doc = {
                        "id": page.replace('.html', ''),
                        "title": soup.find('title').text if soup.find('title') else page,
                        "content": text,
                        "page_type": self._get_page_type(page)
                    }
                    documents.append(doc)
                    
            except Exception as e:
                print(f"Error crawling {page}: {e}")
                
        self.documents = documents
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
        self.documents = documents
    
    def search_documents(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            content_lower = doc['content'].lower()
            if any(word in content_lower for word in query_lower.split()):
                results.append(doc)
        
        return results[:5]  # Return top 5 results