# InfoChatAgent: Web Scraping + RAG Agent

A Python-based agent that scrapes web pages or local HTML files, builds a vector index, and answers questions using RAG (Retrieval-Augmented Generation).

## Features
- Scrape static web pages (URLs) and/or local HTML files
- Clean and extract main content (title, text) using Readability + BeautifulSoup
- Chunk text and embed with Sentence-Transformers
- Build a FAISS vector index on disk
- Ask questions against the index; optionally use OpenAI for generation
- Simple CLI: `scrape`, `index`, `ask`

## Quickstart

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Configure environment:
- Copy `.env.sample` to `.env` and set `OPENAI_API_KEY` if you want LLM-generated answers.

```bash
cp .env.sample .env
# edit .env to add your OpenAI API key
```

4. Scrape content from URLs or local HTML:

```bash
# Scrape two URLs to a docstore jsonl
python cli.py scrape \
  --url https://example.com \
  --url https://www.gutenberg.org/files/1342/1342-h/1342-h.htm \
  --output data/docstore.jsonl

# Or scrape a directory of local .html files
python cli.py scrape \
  --html-dir path/to/htmls \
  --output data/docstore.jsonl
```

5. Build an index from the docstore:

```bash
python cli.py index \
  --docstore data/docstore.jsonl \
  --index-dir indexes/default
```

6. Ask questions:

```bash
# Without OpenAI key, returns a concise extractive answer and top sources
python cli.py ask \
  --index-dir indexes/default \
  --question "What is the main topic?"

# With OpenAI configured, generates an answer with citations
python cli.py ask \
  --index-dir indexes/default \
  --question "Summarize the key points and provide citations." \
  --model gpt-4o-mini
```

## Project Structure

```
.
├── cli.py
├── requirements.txt
├── README.md
├── .env.sample
├── data/
├── indexes/
└── src/
    └── infochat_agent/
        ├── __init__.py
        ├── config.py
        ├── scrape.py
        ├── processing.py
        ├── store.py
        ├── embeddings.py
        ├── index.py
        └── rag.py
```

## Notes
- The scraper handles static pages. For heavy JS sites, consider adding Playwright.
- The default embedding model is `all-MiniLM-L6-v2` via `sentence-transformers`, which is light and fast.
- FAISS indexes and metadata are stored in `--index-dir`.
- For OpenAI generation, set `OPENAI_API_KEY` in `.env` and choose a `--model`.

## Docker (Optional)

Build and run the Streamlit app in Docker:

```
docker build -t infochatagent:latest .
docker run --rm -p 8501:8501 infochatagent:latest
```

Open http://localhost:8501 and follow the same steps as in Quickstart.

## Submission Bundle

To prepare a ZIP for submission:

```
zip -r infochatagent_poc.zip src app.py cli.py requirements.txt .env.sample README.md docs Dockerfile
```

## License
MIT
