# InfoChatAgent Usage Guide

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Optional: Configure OpenAI

```bash
# Copy environment template
copy .env.sample .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_key_here
```

### 3. Run Streamlit UI

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Using the Streamlit UI

1. **Enter a URL** in the sidebar (StackOverflow tag pages work great)
2. **Enable "Follow links"** to scrape question pages
3. **Click "Scrape & Build Index"** and wait for completion
4. **Ask questions** in the chat interface
5. **View answers** with sources and relevant passages

## Using the CLI

### Scrape Web Pages

```bash
# Scrape single URL
python cli.py scrape --url https://stackoverflow.com/questions/tagged/python --output data/python.jsonl

# Scrape multiple URLs with link following
python cli.py scrape \
  --url https://stackoverflow.com/questions/tagged/python \
  --follow-links \
  --link-limit 20 \
  --output data/python_extended.jsonl

# Scrape local HTML files
python cli.py scrape --html-dir path/to/html/files --output data/local.jsonl
```

### Build Index

```bash
# Build index from docstore
python cli.py index --docstore data/python.jsonl --index-dir indexes/python
```

### Ask Questions

```bash
# Ask with extractive answers
python cli.py ask --index-dir indexes/python --question "What are common Python errors?"

# Ask with OpenAI generation (requires API key)
python cli.py ask \
  --index-dir indexes/python \
  --question "Summarize the main Python issues" \
  --model gpt-4o-mini

# Interactive mode
python cli.py ask --index-dir indexes/python
```

## Example Workflows

### StackOverflow Analysis

```bash
# 1. Scrape Python questions
python cli.py scrape \
  --url https://stackoverflow.com/questions/tagged/python \
  --follow-links \
  --link-limit 15 \
  --output data/python_so.jsonl

# 2. Build index
python cli.py index --docstore data/python_so.jsonl --index-dir indexes/python_so

# 3. Ask questions
python cli.py ask --index-dir indexes/python_so --question "What are the most common Python debugging issues?"
```

### Documentation Analysis

```bash
# 1. Scrape documentation
python cli.py scrape \
  --url https://docs.python.org/3/tutorial/ \
  --output data/python_docs.jsonl

# 2. Build index
python cli.py index --docstore data/python_docs.jsonl --index-dir indexes/python_docs

# 3. Query documentation
python cli.py ask --index-dir indexes/python_docs --question "How do I handle exceptions in Python?"
```

## Docker Usage

```bash
# Build image
docker build -t infochatagent .

# Run container
docker run -p 8501:8501 infochatagent

# Run with environment file
docker run -p 8501:8501 --env-file .env infochatagent
```

## Configuration Options

Edit `.env` file or set environment variables:

```bash
# OpenAI settings
OPENAI_API_KEY=your_key_here

# Embedding model (sentence-transformers)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Chunking settings
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Retrieval settings
TOP_K=5
MMR_DIVERSITY=0.7
```

## Troubleshooting

### Common Issues

1. **"No module named 'src'"**
   - Make sure you're running from the project root directory
   - Check that `src/infochat_agent/__init__.py` exists

2. **Scraping fails**
   - Check internet connection
   - Some sites may block automated requests
   - Try different URLs or enable link following

3. **OpenAI errors**
   - Verify API key in `.env` file
   - Check API quota and billing
   - Try different models (gpt-3.5-turbo, gpt-4o-mini)

4. **Memory issues with large documents**
   - Reduce `CHUNK_SIZE` in config
   - Limit number of links to follow
   - Process documents in smaller batches

### Performance Tips

1. **For better scraping:**
   - Use StackOverflow tag pages with link following
   - Limit links to 10-20 for faster processing
   - Cache is enabled by default for repeated requests

2. **For better answers:**
   - Use OpenAI generation for fluent responses
   - Increase `TOP_K` for more context
   - Adjust `MMR_DIVERSITY` for result variety

3. **For faster indexing:**
   - Use smaller embedding models
   - Reduce chunk overlap
   - Process fewer documents initially

## Advanced Usage

### Custom Embedding Models

```python
from src.infochat_agent.embeddings import EmbeddingModel

# Use different model
embedder = EmbeddingModel("sentence-transformers/all-mpnet-base-v2")
```

### Custom Processing

```python
from src.infochat_agent.processing import TextProcessor

# Custom chunking
processor = TextProcessor(chunk_size=256, chunk_overlap=25)
```

### Programmatic Usage

```python
from src.infochat_agent.rag import RAGPipeline

# Load existing index
rag = RAGPipeline("indexes/my_index")

# Ask questions
response = rag.ask("What is the main topic?")
print(response['answer'])
```