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
    """Serve the main HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/{page_name}", response_class=HTMLResponse)
async def serve_page(request: Request, page_name: str):
    """Serve individual HTML pages"""
    if not page_name.endswith('.html'):
        page_name += '.html'
    
    try:
        return templates.TemplateResponse(page_name, {"request": request})
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

# Add chat widget to HTML pages
chat_widget_html = """
<div id="chat-widget" style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
    <div id="chat-button" onclick="toggleChat()" style="
        width: 60px; height: 60px; border-radius: 50%; 
        background: #0056b3; color: white; border: none; 
        cursor: pointer; display: flex; align-items: center; 
        justify-content: center; font-size: 24px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
        💬
    </div>
    
    <div id="chat-window" style="
        display: none; width: 350px; height: 500px; 
        background: white; border: 1px solid #ddd; 
        border-radius: 10px; position: absolute; 
        bottom: 70px; right: 0; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
        
        <div style="background: #0056b3; color: white; padding: 15px; border-radius: 10px 10px 0 0;">
            <h4 style="margin: 0;">TATA Motors Assistant</h4>
        </div>
        
        <div id="chat-messages" style="
            height: 350px; overflow-y: auto; padding: 10px; 
            border-bottom: 1px solid #eee;">
            <div style="padding: 10px; background: #f8f9fa; border-radius: 5px; margin-bottom: 10px;">
                Hello! I'm your TATA Motors assistant. Ask me about vehicles, pricing, offers, or any other information.
            </div>
        </div>
        
        <div style="padding: 10px;">
            <input type="text" id="chat-input" placeholder="Type your message..." 
                style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"
                onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()" style="
                width: 100%; margin-top: 10px; padding: 10px; 
                background: #0056b3; color: white; border: none; 
                border-radius: 5px; cursor: pointer;">Send</button>
        </div>
    </div>
</div>

<script>
function toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.style.display = chatWindow.style.display === 'none' ? 'block' : 'none';
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    messages.innerHTML += `<div style="text-align: right; margin: 10px 0;">
        <div style="background: #0056b3; color: white; padding: 8px 12px; border-radius: 15px; display: inline-block; max-width: 80%;">
            ${message}
        </div>
    </div>`;
    
    input.value = '';
    messages.scrollTop = messages.scrollHeight;
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: message})
        });
        
        const data = await response.json();
        
        // Add bot response
        messages.innerHTML += `<div style="margin: 10px 0;">
            <div style="background: #f8f9fa; padding: 8px 12px; border-radius: 15px; display: inline-block; max-width: 80%;">
                ${data.response}
            </div>
        </div>`;
        
    } catch (error) {
        messages.innerHTML += `<div style="margin: 10px 0;">
            <div style="background: #f8d7da; color: #721c24; padding: 8px 12px; border-radius: 15px; display: inline-block; max-width: 80%;">
                Sorry, I'm having trouble connecting. Please try again.
            </div>
        </div>`;
    }
    
    messages.scrollTop = messages.scrollHeight;
}
</script>
"""

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)