"""Configuration management for InfoChatAgent"""

import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Config(BaseModel):
    # OpenAI settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    default_model: str = "gpt-4o-mini"
    
    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Chunking settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Retrieval settings
    top_k: int = 5
    mmr_diversity: float = 0.7
    
    # Scraping settings
    max_links_to_follow: int = 10
    request_timeout: int = 30
    
    # Storage paths
    default_docstore: str = "data/docstore.jsonl"
    default_index_dir: str = "indexes/default"

config = Config()