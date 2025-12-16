# TATA Motors AI Agent System

A complete AI agent system using LangGraph, MCP Server, Ollama, and FastAPI for TATA Motors website interaction.

## Features

- **LangGraph Agent**: Intelligent conversation flow management
- **MCP Server**: Model Context Protocol for tool integration
- **Ollama Integration**: Local LLM for natural language processing
- **Web Crawling RAG**: Retrieval-Augmented Generation from HTML documents
- **FastAPI Backend**: RESTful API with chat interface
- **Vector Database**: ChromaDB for document embeddings
- **Interactive Chat Widget**: Embedded in all HTML pages

## Architecture

```
User → HTML Pages → FastAPI → LangGraph Agent → MCP Server → Tools
                                     ↓
                              Ollama LLM ← Vector DB (ChromaDB)
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install and Setup Ollama
```bash
# Install Ollama (visit https://ollama.ai)
ollama pull llama3.2
```

### 3. Initialize System
```bash
python setup.py
```

### 4. Start the Server
```bash
python fastapi_server.py
```

### 5. Access the Application
Open browser to: `http://localhost:8000`

## API Endpoints

- `GET /` - Main homepage
- `GET /{page_name}` - Serve HTML pages
- `POST /api/chat` - Chat with AI agent
- `GET /api/health` - Health check
- `POST /api/initialize` - Reinitialize knowledge base

## Available Tools (MCP Server)

1. **search_documents** - Search through TATA Motors documents
2. **get_vehicle_info** - Get vehicle specifications and features
3. **get_pricing** - Get pricing information
4. **get_offers** - Get current offers and promotions
5. **get_contact_info** - Get contact and dealer information

## Usage Examples

### Chat Queries
- "What is the price of Nexon?"
- "Tell me about Harrier features"
- "What are the current offers?"
- "How can I contact TATA Motors?"
- "Compare Nexon and Punch"

### API Usage
```python
import requests

response = requests.post("http://localhost:8000/api/chat", 
    json={"message": "What is the price of TATA Nexon?"})
print(response.json())
```

## File Structure

```
InfoChatAgent/
├── Sample_Html_Car_Sales/     # HTML pages with TATA logo
├── web_crawler.py             # Web crawling and RAG
├── mcp_server.py             # MCP server implementation
├── langgraph_agent.py        # LangGraph agent
├── fastapi_server.py         # FastAPI backend
├── setup.py                  # System initialization
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## Key Components

### Web Crawler
- Crawls HTML pages from Sample_Html_Car_Sales folder
- Extracts text content using BeautifulSoup
- Creates embeddings using SentenceTransformers
- Stores in ChromaDB vector database

### MCP Server
- Implements Model Context Protocol
- Provides tools for document search and information retrieval
- Handles tool execution and response formatting

### LangGraph Agent
- Manages conversation flow
- Determines when to use tools vs direct LLM response
- Integrates with Ollama for natural language generation
- Processes tool results and generates final responses

### FastAPI Server
- Serves HTML pages with embedded chat widget
- Provides REST API for chat functionality
- Handles real-time communication with the agent

## Troubleshooting

1. **Ollama not found**: Ensure Ollama is installed and running
2. **Model not available**: Run `ollama pull llama3.2`
3. **Port conflicts**: Change port in fastapi_server.py
4. **ChromaDB issues**: Delete `chroma_db` folder and run setup again

## Customization

- Modify `langgraph_agent.py` to add new conversation flows
- Update `mcp_server.py` to add new tools
- Customize chat widget in `fastapi_server.py`
- Add new HTML pages to Sample_Html_Car_Sales folder