import streamlit as st
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re

# Page config
st.set_page_config(
    page_title="RAG Agent Chat",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left: 5px solid #4caf50;
    }
    .source-tag {
        background-color: #fff3cd;
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'scraped_urls' not in st.session_state:
    st.session_state.scraped_urls = []
if 'show_history' not in st.session_state:
    st.session_state.show_history = False

class RAGAgent:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = None
        self.index = None
        self.media_items = []  # Store images, videos, etc.
        
    def scrape_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract images
            images = soup.find_all('img')
            for img in images:
                img_src = img.get('src', '')
                img_alt = img.get('alt', 'Image')
                if img_src and len(img_alt) > 3:  # Filter out empty alt tags
                    if img_src.startswith('/'):
                        img_src = url.rsplit('/', 1)[0] + img_src
                    elif not img_src.startswith('http'):
                        img_src = url.rsplit('/', 1)[0] + '/' + img_src
                    
                    self.media_items.append({
                        'type': 'image',
                        'url': img_src,
                        'alt': img_alt,
                        'source': url
                    })
                    
                    self.documents.append({
                        'text': f"Image: {img_alt}",
                        'source': url,
                        'title': 'Image',
                        'media_url': img_src,
                        'media_type': 'image'
                    })
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'button', 'form', 'input']):
                element.decompose()
            
            title = soup.title.string if soup.title else url
            
            chunks = []
            
            # Process error sections with complete context
            error_sections = soup.find_all(['div', 'section'], class_=['error-section', 'handbook'])
            
            for section in error_sections:
                # Get heading
                heading = section.find(['h3', 'h4'])
                heading_text = heading.get_text(strip=True) if heading else ''
                
                # Get error code
                error_match = re.search(r'(EV\d{3}|P\d{4}|U\d{4})', section.get_text())
                if error_match:
                    error_code = error_match.group(1)
                    
                    # Get symptoms
                    symptoms = []
                    symptom_section = section.find(string=re.compile('Symptoms?:', re.I))
                    if symptom_section:
                        symptom_list = symptom_section.find_next('ul')
                        if symptom_list:
                            symptoms = [li.get_text(strip=True) for li in symptom_list.find_all('li')]
                    
                    # Get resolution steps
                    steps = []
                    steps_section = section.find(string=re.compile('Resolution Steps?:', re.I))
                    if steps_section:
                        steps_list = steps_section.find_next('ol')
                        if steps_list:
                            steps = [li.get_text(strip=True) for li in steps_list.find_all('li')]
                    
                    # Create structured chunk
                    chunk = f"Error Code {error_code}: {heading_text}\n"
                    if symptoms:
                        chunk += "Symptoms: " + "; ".join(symptoms[:3]) + "\n"
                    if steps:
                        chunk += "Resolution: " + " ".join(steps[:5])
                    
                    chunks.append(chunk.strip())
            
            # Extract main content paragraphs
            main_content = soup.find(['main', 'article']) or soup.find('body')
            if main_content:
                paragraphs = main_content.find_all(['p', 'li'])
                
                current_heading = ""
                for elem in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li']):
                    text = elem.get_text(separator=' ', strip=True)
                    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                    
                    if len(text) < 15:  # Skip very short text
                        continue
                    
                    # Update heading context
                    if elem.name in ['h1', 'h2', 'h3', 'h4']:
                        current_heading = text
                        continue
                    
                    # Filter out navigation/menu items and competitor brands
                    competitor_brands = ['mahindra', 'toyota', 'hyundai', 'maruti', 'honda', 'kia', 'mg', 'nissan', 'renault', 'volkswagen', 'skoda', 'jeep', 'ford']
                    if any(word in text.lower() for word in ['home', 'contact', 'login', 'sign in', 'menu', 'search']):
                        if len(text) < 50:
                            continue
                    
                    # Skip competitor brand mentions
                    if any(brand in text.lower() for brand in competitor_brands):
                        continue
                    
                    # Skip price comparison text
                    if 'show price in my city' in text.lower() or 'avg. ex-showroom' in text.lower():
                        continue
                    
                    # Create focused chunks for error codes
                    if re.search(r'(EV\d{3}|P\d{4}|U\d{4})', text, re.IGNORECASE):
                        chunk = f"{current_heading}: {text}" if current_heading else text
                        chunks.append(chunk)
                    elif len(text) > 40:  # Only substantial content
                        chunk = f"{current_heading}: {text}" if current_heading else text
                        chunks.append(chunk)
            
            # Add chunks to documents
            for chunk in chunks:
                self.documents.append({
                    'text': chunk,
                    'source': url,
                    'title': title,
                    'media_url': None,
                    'media_type': None
                })
            
            return True, f"✅ Scraped {len(chunks)} text chunks and {len(self.media_items)} media items"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def build_index(self):
        if not self.documents:
            return False
        
        texts = [doc['text'] for doc in self.documents]
        self.embeddings = self.model.encode(texts)
        
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
        
        return True
    
    def ask(self, question, top_k=10):
        if self.index is None:
            return []
        
        # Extract error code from question if present
        error_code_pattern = r'\b(EV\d{3}|P\d{4}|U\d{4})\b'
        error_codes = re.findall(error_code_pattern, question.upper())
        
        # First, try exact keyword matching for error codes
        if error_codes:
            exact_matches = []
            for i, doc in enumerate(self.documents):
                for code in error_codes:
                    if code in doc['text'].upper():
                        exact_matches.append({
                            'text': doc['text'],
                            'source': doc['source'],
                            'relevance': 0.0,
                            'media_url': doc.get('media_url'),
                            'media_type': doc.get('media_type')
                        })
                        break
            
            if exact_matches:
                # Remove duplicates and return exact matches first
                seen = set()
                unique_matches = []
                for match in exact_matches:
                    if match['text'][:100] not in seen:
                        seen.add(match['text'][:100])
                        unique_matches.append(match)
                return unique_matches[:5]
        
        # Fallback to semantic search
        question_embedding = self.model.encode([question])
        distances, indices = self.index.search(question_embedding.astype('float32'), top_k)
        
        results = []
        seen_texts = set()
        
        for idx, distance in zip(indices[0], distances[0]):
            doc = self.documents[idx]
            text = doc['text']
            
            # Avoid duplicate results
            if text[:100] in seen_texts:
                continue
            seen_texts.add(text[:100])
            
            # Check relevance - lower distance is better
            if distance < 1.5:  # Threshold for relevance
                results.append({
                    'text': text,
                    'source': doc['source'],
                    'relevance': float(distance),
                    'media_url': doc.get('media_url'),
                    'media_type': doc.get('media_type')
                })
        
        return results
    
    def format_response(self, results):
        """Format results into a clear, structured response with images"""
        if not results:
            return None, []
        
        response = "### 📋 Answer:\n\n"
        images_to_display = []
        
        # Get the most relevant result
        best_result = results[0]
        response += f"{best_result['text']}\n\n"
        
        # Collect image if available
        if best_result.get('media_type') == 'image' and best_result.get('media_url'):
            images_to_display.append(best_result['media_url'])
        
        # Add additional context if available
        if len(results) > 1:
            response += "\n### 📚 Additional Information:\n\n"
            for i, result in enumerate(results[1:3], 1):  # Show max 2 more
                response += f"**{i}.** {result['text'][:300]}...\n\n"
                
                # Collect images for additional results too
                if result.get('media_type') == 'image' and result.get('media_url'):
                    images_to_display.append(result['media_url'])
        
        # Add sources
        response += "\n### 🔗 Sources:\n"
        unique_sources = list(set([r['source'] for r in results]))
        for source in unique_sources:
            response += f"- {source}\n"
        
        return response, images_to_display

# Header
st.title("🤖 RAG Agent Chat")
st.markdown("### Scrape any webpage and chat with its content")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    url_input = st.text_input("Enter URL to scrape:", placeholder="https://example.com")
    
    if st.button("🔍 Scrape URL", use_container_width=True):
        if url_input:
            with st.spinner("Scraping URL..."):
                if st.session_state.agent is None:
                    st.session_state.agent = RAGAgent()
                
                success, message = st.session_state.agent.scrape_url(url_input)
                
                if success:
                    st.session_state.agent.build_index()
                    st.session_state.scraped_urls.append(url_input)
                    st.success(message)
                else:
                    st.error(message)
        else:
            st.warning("Please enter a URL")
    
    st.divider()
    
    if st.session_state.scraped_urls:
        st.subheader("📚 Scraped URLs")
        for url in st.session_state.scraped_urls:
            st.markdown(f"✓ {url}")
    
    st.divider()
    
    if st.button("🔄 Reset Chat", use_container_width=True):
        st.session_state.agent = None
        st.session_state.chat_history = []
        st.session_state.scraped_urls = []
        st.session_state.show_history = False
        st.rerun()
    
    if len(st.session_state.chat_history) > 0:
        if st.button("📜 View Chat History", use_container_width=True):
            st.session_state.show_history = not st.session_state.show_history
            st.rerun()

# Main chat area
st.divider()

# Show chat history if toggled
if st.session_state.show_history and len(st.session_state.chat_history) > 2:
    with st.expander("📜 Chat History", expanded=True):
        for i in range(0, len(st.session_state.chat_history) - 2, 2):
            if i < len(st.session_state.chat_history):
                st.markdown(f"**Q:** {st.session_state.chat_history[i]['content']}")
            if i + 1 < len(st.session_state.chat_history):
                st.markdown(f"**A:** {st.session_state.chat_history[i + 1]['content'][:200]}...")
            st.divider()

# Display only the last question and answer
if len(st.session_state.chat_history) >= 2:
    last_question = st.session_state.chat_history[-2]
    last_answer = st.session_state.chat_history[-1]
    
    st.markdown(f"""
    <div class="chat-message user-message">
        <strong>👤 You:</strong><br>
        {last_question['content']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="chat-message bot-message">
        <strong>🤖 Agent:</strong><br>
        {last_answer['content']}
    </div>
    """, unsafe_allow_html=True)
    
    # Display images if available
    if 'images' in last_answer and last_answer['images']:
        st.markdown("### 🖼️ Related Images:")
        cols = st.columns(min(len(last_answer['images']), 3))
        for idx, img_url in enumerate(last_answer['images']):
            with cols[idx % 3]:
                try:
                    st.image(img_url, use_container_width=True)
                except:
                    st.warning(f"Could not load image: {img_url}")
                    
elif len(st.session_state.chat_history) == 1:
    st.markdown(f"""
    <div class="chat-message user-message">
        <strong>👤 You:</strong><br>
        {st.session_state.chat_history[0]['content']}
    </div>
    """, unsafe_allow_html=True)

# Chat input
question = st.chat_input("Ask a question about the scraped content...")

if question:
    # Add user message
    st.session_state.chat_history.append({
        'role': 'user',
        'content': question
    })
    
    # Get response
    if st.session_state.agent is None or not st.session_state.agent.documents:
        response = "⚠️ Please scrape a URL first before asking questions."
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response
        })
    else:
        with st.spinner("Thinking..."):
            results = st.session_state.agent.ask(question, top_k=5)
            
            if results:
                response, images = st.session_state.agent.format_response(results)
            else:
                response = "❌ No relevant information found. Try rephrasing your question or scrape more URLs."
                images = []
            
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response,
                'images': images
            })
    
    st.rerun()

# Footer
if not st.session_state.scraped_urls:
    st.info("👈 Start by scraping a URL from the sidebar, then ask questions!")
