"""Streamlit UI for InfoChatAgent"""

import streamlit as st
import os
import tempfile
from src.infochat_agent.scrape import WebScraper, save_docstore
from src.infochat_agent.index import build_index_from_docstore
from src.infochat_agent.rag import RAGPipeline
from src.infochat_agent.config import config

# Page config
st.set_page_config(
    page_title="InfoChatAgent",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'index_built' not in st.session_state:
    st.session_state.index_built = False
if 'index_dir' not in st.session_state:
    st.session_state.index_dir = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Title and description
st.title("🤖 InfoChatAgent")
st.markdown("**Web Scraping + RAG Agent** - Scrape web pages and ask questions with AI-powered answers")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Scraping options
    st.subheader("📄 Scraping")
    url_input = st.text_input(
        "Target URL", 
        value="https://stackoverflow.com/questions/tagged/python",
        help="URL to scrape (StackOverflow tag pages work best)"
    )
    
    follow_links = st.checkbox(
        "Follow top StackOverflow question links", 
        value=True,
        help="Extract and scrape question links from StackOverflow tag pages"
    )
    
    link_limit = st.slider(
        "Max links to follow", 
        min_value=1, 
        max_value=50, 
        value=10,
        help="Number of question links to follow and scrape"
    )
    
    # Build index button
    if st.button("🔨 Scrape & Build Index", type="primary"):
        with st.spinner("Scraping and building index..."):
            try:
                # Create temporary directories
                temp_dir = tempfile.mkdtemp()
                docstore_path = os.path.join(temp_dir, "docstore.jsonl")
                index_dir = os.path.join(temp_dir, "index")
                
                # Scrape
                scraper = WebScraper()
                documents = scraper.scrape_multiple([url_input], follow_links, link_limit)
                
                if documents:
                    # Save docstore
                    save_docstore(documents, docstore_path)
                    
                    # Build index
                    build_index_from_docstore(docstore_path, index_dir)
                    
                    # Update session state
                    st.session_state.index_built = True
                    st.session_state.index_dir = index_dir
                    st.session_state.documents_count = len(documents)
                    
                    st.success(f"✅ Successfully scraped {len(documents)} documents and built index!")
                else:
                    st.error("❌ No documents were scraped. Please check the URL.")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Query options
    st.subheader("🔍 Query Settings")
    use_llm = st.checkbox(
        "Use OpenAI for generation", 
        value=bool(config.openai_api_key),
        help="Generate fluent answers with OpenAI (requires API key in .env)"
    )
    
    top_k = st.slider(
        "Number of results", 
        min_value=1, 
        max_value=20, 
        value=config.top_k,
        help="Number of relevant passages to retrieve"
    )

# Main content area
if not st.session_state.index_built:
    st.info("👈 Please scrape a URL and build an index first using the sidebar.")
    
    # Show example
    st.subheader("How it works:")
    st.markdown("""
    1. **Scrape**: Enter a URL (StackOverflow tag pages work great)
    2. **Index**: The system will extract clean text, chunk it, and build a vector index
    3. **Ask**: Query the indexed content with natural language questions
    4. **Get Answers**: Receive AI-powered responses with citations and sources
    """)
    
    st.subheader("Example URLs to try:")
    st.code("https://stackoverflow.com/questions/tagged/python")
    st.code("https://stackoverflow.com/questions/tagged/javascript")
    st.code("https://stackoverflow.com/questions/tagged/machine-learning")

else:
    # Chat interface
    st.subheader(f"💬 Chat with your indexed content ({st.session_state.documents_count} documents)")
    
    # Display chat history
    for i, (question, response) in enumerate(st.session_state.chat_history):
        with st.container():
            st.markdown(f"**Q{i+1}:** {question}")
            
            # Answer
            st.markdown("**Answer:**")
            st.info(response['answer'])
            
            # Insights
            if response.get('insights', {}).get('common_terms'):
                with st.expander("🔍 Top Insights"):
                    terms = response['insights']['common_terms'][:5]
                    terms_str = ", ".join([f"**{term}** ({count})" for term, count in terms])
                    st.markdown(f"**Common terms:** {terms_str}")
                    st.markdown(f"**Sources:** {response['insights']['sources_count']}")
            
            # Sources
            if response.get('sources'):
                with st.expander("📚 Sources"):
                    for j, (title, url) in enumerate(response['sources'], 1):
                        st.markdown(f"{j}. **{title}**")
                        st.markdown(f"   🔗 [{url}]({url})")
            
            # Passages
            if response.get('passages'):
                with st.expander("📄 Relevant Passages"):
                    for j, passage in enumerate(response['passages'][:3], 1):
                        st.markdown(f"**{j}. {passage['source']}** (score: {passage['score']:.3f})")
                        st.markdown(f"> {passage['text']}")
            
            st.divider()
    
    # Question input
    question = st.text_input(
        "Ask a question about the scraped content:",
        placeholder="What are the common Python issues discussed?",
        key="question_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("🚀 Ask", type="primary")
    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state.chat_history = []
            st.rerun()
    
    if ask_button and question:
        with st.spinner("Searching and generating answer..."):
            try:
                # Initialize RAG pipeline
                rag = RAGPipeline(st.session_state.index_dir)
                
                # Get answer
                response = rag.ask(question, use_llm=use_llm, top_k=top_k)
                
                # Add to chat history
                st.session_state.chat_history.append((question, response))
                
                # Clear input and rerun
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ using Streamlit, FAISS, Sentence-Transformers, and OpenAI. "
    "Configure your OpenAI API key in `.env` for enhanced generation."
)