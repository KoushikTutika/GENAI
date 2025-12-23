"""Web scraping functionality with readability and BeautifulSoup"""

import requests
import json
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from readability import Document
import time
from tqdm import tqdm
import requests_cache
from .config import config

# Enable caching for requests
requests_cache.install_cache('scrape_cache', expire_after=3600)

class WebScraper:
    def __init__(self, timeout: int = None):
        self.timeout = timeout or config.request_timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_url(self, url: str) -> Optional[Dict]:
        """Scrape a single URL and extract clean content"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Use readability to extract main content
            doc = Document(response.text)
            title = doc.title()
            content = doc.summary()
            
            # Clean with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            
            return {
                'url': url,
                'title': title,
                'content': text,
                'length': len(text)
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def get_stackoverflow_links(self, tag_url: str, limit: int = 10) -> List[str]:
        """Extract question links from StackOverflow tag page"""
        try:
            response = self.session.get(tag_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            # Find question links
            for link in soup.find_all('a', class_='s-link'):
                href = link.get('href')
                if href and '/questions/' in href:
                    full_url = urljoin(tag_url, href)
                    links.append(full_url)
                    if len(links) >= limit:
                        break
            
            return links
        except Exception as e:
            print(f"Error getting links from {tag_url}: {e}")
            return []
    
    def scrape_multiple(self, urls: List[str], follow_links: bool = False, 
                       link_limit: int = 10) -> List[Dict]:
        """Scrape multiple URLs with optional link following"""
        results = []
        
        for url in tqdm(urls, desc="Scraping URLs"):
            # Scrape main URL
            result = self.scrape_url(url)
            if result:
                results.append(result)
            
            # Follow links if enabled and it's a StackOverflow tag page
            if follow_links and 'stackoverflow.com/questions/tagged/' in url:
                links = self.get_stackoverflow_links(url, link_limit)
                for link in tqdm(links, desc=f"Following links from {url}", leave=False):
                    link_result = self.scrape_url(link)
                    if link_result:
                        results.append(link_result)
                    time.sleep(0.5)  # Rate limiting
        
        return results
    
    def scrape_html_files(self, html_dir: str) -> List[Dict]:
        """Scrape local HTML files"""
        import os
        results = []
        
        for filename in os.listdir(html_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(html_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc = Document(content)
                    title = doc.title() or filename
                    clean_content = doc.summary()
                    
                    soup = BeautifulSoup(clean_content, 'html.parser')
                    text = soup.get_text(separator=' ', strip=True)
                    
                    results.append({
                        'url': f'file://{filepath}',
                        'title': title,
                        'content': text,
                        'length': len(text)
                    })
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
        
        return results

def save_docstore(documents: List[Dict], output_path: str):
    """Save documents to JSONL format"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')

def load_docstore(docstore_path: str) -> List[Dict]:
    """Load documents from JSONL format"""
    documents = []
    with open(docstore_path, 'r', encoding='utf-8') as f:
        for line in f:
            documents.append(json.loads(line.strip()))
    return documents