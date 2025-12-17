from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import asyncio
from langgraph_agent import TATAMotorsAgent
import uvicorn
import os

app = FastAPI(title="TATA Motors AI Agent", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="Sample_Html_Car_Sales"), name="static")

# Templates
templates = Jinja2Templates(directory="Sample_Html_Car_Sales")

# Initialize agent
agent = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str

@app.on_event("startup")
async def startup_event():
    global agent
    print("Initializing TATA Motors Agent...")
    agent = TATAMotorsAgent()
    print("Agent initialized successfully!")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main HTML page with chat widget"""
    try:
        # Read the HTML file
        file_path = "Sample_Html_Car_Sales/index.html"
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inject chat widget before closing body tag
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', chat_widget_html + '</body>')
        else:
            html_content += chat_widget_html
        
        return HTMLResponse(content=html_content)
    except:
        return HTMLResponse(content="<h1>Welcome to TATA Motors</h1>" + chat_widget_html)

@app.get("/{page_name}", response_class=HTMLResponse)
async def serve_page(request: Request, page_name: str):
    """Serve individual HTML pages with chat widget"""
    if not page_name.endswith('.html'):
        page_name += '.html'
    
    try:
        # Read the HTML file
        file_path = f"Sample_Html_Car_Sales/{page_name}"
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inject chat widget before closing body tag
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', chat_widget_html + '</body>')
        else:
            html_content += chat_widget_html
        
        return HTMLResponse(content=html_content)
    except:
        raise HTTPException(status_code=404, detail="Page not found")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """Chat endpoint for AI agent interaction"""
    try:
        if not agent:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        response = await agent.process_query(chat_request.message)
        
        return ChatResponse(
            response=response,
            status="success"
        )
    except Exception as e:
        return ChatResponse(
            response=f"Sorry, I encountered an error: {str(e)}",
            status="error"
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent_ready": agent is not None}

@app.post("/api/initialize")
async def initialize_knowledge_base():
    """Manually trigger knowledge base initialization"""
    try:
        if agent:
            agent._initialize_knowledge_base()
            return {"status": "success", "message": "Knowledge base reinitialized"}
        else:
            return {"status": "error", "message": "Agent not available"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Add modern chat widget to HTML pages
chat_widget_html = """
<style>
@keyframes slideUp {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}
#chat-button:hover {
    animation: pulse 0.5s ease-in-out;
    background: linear-gradient(135deg, #0056b3 0%, #003d82 100%);
}
.typing-indicator {
    display: inline-block;
    padding: 10px 15px;
    background: #f0f0f0;
    border-radius: 15px;
}
.typing-indicator span {
    height: 8px;
    width: 8px;
    background: #999;
    border-radius: 50%;
    display: inline-block;
    margin: 0 2px;
    animation: typing 1.4s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-10px); }
}
</style>

<div id="chat-widget" style="position: fixed; bottom: 20px; right: 20px; z-index: 10000; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div id="chat-button" onclick="toggleChat()" style="
        width: 70px; height: 70px; border-radius: 50%; 
        background: linear-gradient(135deg, #0056b3 0%, #004494 100%);
        color: white; border: none; cursor: pointer; 
        display: flex; align-items: center; justify-content: center; 
        font-size: 32px; box-shadow: 0 6px 20px rgba(0,86,179,0.4);
        transition: all 0.3s ease;">
        💬
    </div>
    
    <div id="chat-window" style="
        display: none; width: 400px; height: 600px; 
        background: white; border: none;
        border-radius: 20px; position: absolute; 
        bottom: 85px; right: 0; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        animation: slideUp 0.3s ease-out;
        overflow: hidden;">
        
        <div style="
            background: linear-gradient(135deg, #0056b3 0%, #004494 100%);
            color: white; padding: 20px; 
            display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; font-size: 20px; font-weight: 600;">🚗 TATA Motors AI</h3>
                <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.9;">Your Virtual Assistant</p>
            </div>
            <button onclick="toggleChat()" style="
                background: rgba(255,255,255,0.2); border: none; 
                color: white; font-size: 24px; cursor: pointer; 
                width: 35px; height: 35px; border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                transition: background 0.3s;" 
                onmouseover="this.style.background='rgba(255,255,255,0.3)'" 
                onmouseout="this.style.background='rgba(255,255,255,0.2)'">
                ×
            </button>
        </div>
        
        <div id="chat-messages" style="
            height: 430px; overflow-y: auto; padding: 20px; 
            background: #f8f9fa;">
            <div style="
                padding: 15px; background: white; 
                border-radius: 15px; margin-bottom: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <strong style="color: #0056b3;">👋 Welcome!</strong><br>
                <span style="color: #666; font-size: 14px;">
                    I'm your TATA Motors assistant. Ask me about:<br>
                    • Vehicle specifications & features<br>
                    • Pricing & offers<br>
                    • Brochures & documentation<br>
                    • Contact information
                </span>
            </div>
        </div>
        
        <div style="padding: 15px; background: white; border-top: 1px solid #e0e0e0;">
            <div style="display: flex; gap: 10px;">
                <input type="text" id="chat-input" placeholder="Ask me anything..." 
                    style="
                        flex: 1; padding: 12px 15px; 
                        border: 2px solid #e0e0e0; 
                        border-radius: 25px; font-size: 14px;
                        outline: none; transition: border 0.3s;"
                    onkeypress="if(event.key==='Enter') sendMessage()"
                    onfocus="this.style.borderColor='#0056b3'"
                    onblur="this.style.borderColor='#e0e0e0'">
                <button onclick="sendMessage()" style="
                    padding: 12px 25px; 
                    background: linear-gradient(135deg, #0056b3 0%, #004494 100%);
                    color: white; border: none; 
                    border-radius: 25px; cursor: pointer;
                    font-weight: 600; font-size: 14px;
                    transition: transform 0.2s, box-shadow 0.2s;"
                    onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 4px 12px rgba(0,86,179,0.3)'"
                    onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none'">
                    Send ➤
                </button>
            </div>
        </div>
    </div>
</div>

<script>
function toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    const chatButton = document.getElementById('chat-button');
    if (chatWindow.style.display === 'none') {
        chatWindow.style.display = 'block';
        chatButton.innerHTML = '✕';
    } else {
        chatWindow.style.display = 'none';
        chatButton.innerHTML = '💬';
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    messages.innerHTML += `
        <div style="text-align: right; margin: 15px 0; animation: slideUp 0.3s ease-out;">
            <div style="
                background: linear-gradient(135deg, #0056b3 0%, #004494 100%);
                color: white; padding: 12px 18px; 
                border-radius: 20px 20px 5px 20px;
                display: inline-block; max-width: 75%;
                box-shadow: 0 2px 8px rgba(0,86,179,0.2);
                word-wrap: break-word; text-align: left;">
                ${message}
            </div>
        </div>`;
    
    input.value = '';
    messages.scrollTop = messages.scrollHeight;
    
    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    messages.innerHTML += `
        <div id="${typingId}" style="margin: 15px 0;">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>`;
    messages.scrollTop = messages.scrollHeight;
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: message})
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        document.getElementById(typingId).remove();
        
        // Add bot response
        messages.innerHTML += `
            <div style="margin: 15px 0; animation: slideUp 0.3s ease-out;">
                <div style="
                    background: white; padding: 12px 18px; 
                    border-radius: 20px 20px 20px 5px;
                    display: inline-block; max-width: 75%;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    color: #333; word-wrap: break-word;">
                    ${data.response.replace(/\n/g, '<br>')}
                </div>
            </div>`;
        
    } catch (error) {
        document.getElementById(typingId).remove();
        messages.innerHTML += `
            <div style="margin: 15px 0;">
                <div style="
                    background: #fee; padding: 12px 18px; 
                    border-radius: 20px 20px 20px 5px;
                    display: inline-block; max-width: 75%;
                    color: #c33; border-left: 4px solid #c33;">
                    ⚠️ Connection error. Please try again.
                </div>
            </div>`;
    }
    
    messages.scrollTop = messages.scrollHeight;
}
</script>
"""

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)