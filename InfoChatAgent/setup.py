import asyncio
import os
from web_crawler import WebCrawler

async def setup_system():
    """Setup the complete system"""
    print("🚀 Setting up TATA Motors AI Agent System...")
    
    # 1. Initialize web crawler
    print("📄 Initializing web crawler...")
    crawler = WebCrawler()
    
    # 2. Crawl and index documents
    print("🔍 Crawling HTML documents...")
    documents = crawler.crawl_html_pages()
    print(f"Found {len(documents)} documents")
    
    # 3. Store in vector database
    print("💾 Storing documents in vector database...")
    crawler.store_documents(documents)
    
    print("✅ System setup complete!")
    print("\nTo start the system:")
    print("1. Ensure Ollama is running with llama3.2 model")
    print("2. Run: python fastapi_server.py")
    print("3. Open browser to: http://localhost:8000")
    
    return True

if __name__ == "__main__":
    asyncio.run(setup_system())