# Simple RAG Agent - Streamlit Chat UI

A beautiful chat interface for the RAG agent that scrapes URLs and answers questions.

## Features
- 🎨 Beautiful chat interface with Streamlit
- 🔍 Scrape any URL and extract content
- 💬 Chat-style Q&A interface
- 📚 Multiple URL support
- 🔄 Reset functionality
- 📱 Responsive design

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

2. The app will open in your browser at:
```
http://localhost:8501
```

3. Use the interface:
   - Enter a URL in the sidebar and click "Scrape URL"
   - Ask questions in the chat input at the bottom
   - View responses with relevant passages and sources

## Example URLs to Try
- http://localhost:8080/passenger-cars.html
- http://localhost:8080/electric-vehicles.html
- http://localhost:8080/handbook-nexon.html
- Any public website URL

## Example Questions
- "What are the features of TATA Nexon?"
- "Tell me about electric vehicles"
- "What is the price range?"
- "How to fix error P0420?"
- "What is the battery warranty?"

## Features
- **Chat Interface**: Natural conversation flow
- **Real-time Processing**: Instant responses
- **Source Attribution**: See where information comes from
- **Multiple URLs**: Scrape and query multiple sources
- **Clean Design**: Modern and intuitive UI
