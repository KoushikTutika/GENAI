# TATA Motors AI Agent System - POC Documentation

## Executive Summary

This document provides a comprehensive overview of the TATA Motors AI Agent System, a proof-of-concept implementation that demonstrates an intelligent conversational agent powered by LangGraph, Model Context Protocol (MCP), and FastAPI.

**Key Technologies:**
- LangGraph for agent orchestration
- MCP Server for tool integration
- FastAPI for REST API
- SimpleCrawler for document retrieval
- HTML/CSS/JavaScript for UI

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Web Browser  │  │  Chat Widget │  │  REST API    │      │
│  │ (HTML Pages) │  │  (chat.html) │  │  (curl/code) │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   FastAPI       │
                    │   Server        │
                    │  (Port 8000)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  LangGraph      │
                    │  Agent          │
                    │ (TATAMotorsAgent)│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  MCP Server     │
                    │  (Tool Manager) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ SimpleCrawler   │
                    │ (Document Store)│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  HTML Documents │
                    │ (Sample_Html_   │
                    │  Car_Sales/)    │
                    └─────────────────┘
```

### 1.2 Component Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                          │
│  ┌────────────────────────────────────────────────────┐      │
│  │              fastapi_server.py                      │      │
│  │  • HTTP Request Handling                            │      │
│  │  • Route Management                                 │      │
│  │  • HTML Injection                                   │      │
│  │  • API Endpoints (/api/chat, /api/health)          │      │
│  └────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
                             │
┌──────────────────────────────────────────────────────────────┐
│                    AGENT LAYER                                │
│  ┌────────────────────────────────────────────────────┐      │
│  │           langgraph_agent.py                        │      │
│  │  • Conversation Flow Management                     │      │
│  │  • State Management (AgentState)                    │      │
│  │  • Decision Making (agent_node)                     │      │
│  │  • Tool Invocation (tools_node)                     │      │
│  │  • Graph Compilation                                │      │
│  └────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
                             │
┌──────────────────────────────────────────────────────────────┐
│                    TOOL LAYER                                 │
│  ┌────────────────────────────────────────────────────┐      │
│  │              mcp_server.py                          │      │
│  │  • Tool Registration                                │      │
│  │  • Tool Execution                                   │      │
│  │  • Request Routing                                  │      │
│  │  • Response Formatting                              │      │
│  │                                                      │      │
│  │  Tools:                                             │      │
│  │  • search_documents                                 │      │
│  │  • get_vehicle_info                                 │      │
│  │  • get_pricing                                      │      │
│  │  • get_offers                                       │      │
│  │  • get_contact_info                                 │      │
│  └────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
                             │
┌──────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                 │
│  ┌────────────────────────────────────────────────────┐      │
│  │           simple_crawler.py                         │      │
│  │  • HTML Document Loading                            │      │
│  │  • Text Extraction (BeautifulSoup)                  │      │
│  │  • Keyword-based Search                             │      │
│  │  • Document Storage                                 │      │
│  └────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Agent Flow Diagram

### 2.1 LangGraph Agent Flow

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ User Query  │
                    │ (HumanMsg)  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────────┐
                    │  AGENT NODE     │
                    │                 │
                    │ 1. Analyze Query│
                    │ 2. Check Keywords│
                    │ 3. Decide Action│
                    └──────┬──────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         ┌──────▼──────┐      ┌──────▼──────┐
         │ Needs Tools?│      │ Direct      │
         │    YES      │      │ Response    │
         └──────┬──────┘      │    NO       │
                │             └──────┬──────┘
                │                    │
         ┌──────▼──────────┐         │
         │  TOOLS NODE     │         │
         │                 │         │
         │ 1. Extract Tool │         │
         │ 2. Call MCP     │         │
         │ 3. Get Results  │         │
         │ 4. Format Reply │         │
         └──────┬──────────┘         │
                │                    │
                └──────────┬─────────┘
                           │
                    ┌──────▼──────┐
                    │   END       │
                    │             │
                    │ Return      │
                    │ Response    │
                    └─────────────┘
```

### 2.2 Detailed Agent Decision Flow

```
User Query: "What is the price of Nexon?"
           │
           ▼
    ┌──────────────┐
    │ agent_node() │
    └──────┬───────┘
           │
           ▼
    ┌─────────────────────────┐
    │ _needs_tools(message)   │
    │ Check keywords:         │
    │ ["price", "nexon"]      │
    └──────┬──────────────────┘
           │
           ▼ YES (keywords found)
    ┌─────────────────────────┐
    │ _generate_tool_call()   │
    │                         │
    │ Detected: "price"       │
    │ Vehicle: "nexon"        │
    │                         │
    │ Return:                 │
    │ {                       │
    │   name: "get_pricing",  │
    │   arguments: {          │
    │     vehicle_name: "nexon"│
    │   }                     │
    │ }                       │
    └──────┬──────────────────┘
           │
           ▼
    ┌──────────────┐
    │ tools_node() │
    └──────┬───────┘
           │
           ▼
    ┌─────────────────────────┐
    │ MCP Server Request      │
    │ {                       │
    │   method: "tools/call", │
    │   params: {             │
    │     name: "get_pricing",│
    │     arguments: {...}    │
    │   }                     │
    │ }                       │
    └──────┬──────────────────┘
           │
           ▼
    ┌─────────────────────────┐
    │ Tool Execution          │
    │ (MCP Server)            │
    └──────┬──────────────────┘
           │
           ▼
    ┌─────────────────────────┐
    │ Format Response         │
    │ "Based on TATA Motors   │
    │  information: [result]" │
    └──────┬──────────────────┘
           │
           ▼
    ┌──────────────┐
    │ Return to    │
    │ User         │
    └──────────────┘
```

---

## 3. MCP Server Tool Invocation Flow

### 3.1 MCP Server Architecture

```
┌─────────────────────────────────────────────────────┐
│              MCP SERVER (mcp_server.py)             │
│                                                     │
│  ┌───────────────────────────────────────────┐    │
│  │         Tool Registry                      │    │
│  │  {                                         │    │
│  │    "search_documents": function,           │    │
│  │    "get_vehicle_info": function,           │    │
│  │    "get_pricing": function,                │    │
│  │    "get_offers": function,                 │    │
│  │    "get_contact_info": function            │    │
│  │  }                                         │    │
│  └───────────────────────────────────────────┘    │
│                                                     │
│  ┌───────────────────────────────────────────┐    │
│  │      Request Handler                       │    │
│  │  • handle_request()                        │    │
│  │  • _list_tools()                           │    │
│  │  • _call_tool()                            │    │
│  └───────────────────────────────────────────┘    │
│                                                     │
│  ┌───────────────────────────────────────────┐    │
│  │      SimpleCrawler Instance                │    │
│  │  • crawl_html_pages()                      │    │
│  │  • search_documents()                      │    │
│  │  • store_documents()                       │    │
│  └───────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### 3.2 Tool Invocation Sequence

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│LangGraph │     │   MCP    │     │  Tool    │     │ Crawler  │
│  Agent   │     │  Server  │     │ Function │     │          │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ 1. Tool Call   │                │                │
     │ Request        │                │                │
     ├───────────────>│                │                │
     │                │                │                │
     │                │ 2. Route to    │                │
     │                │    Tool        │                │
     │                ├───────────────>│                │
     │                │                │                │
     │                │                │ 3. Execute     │
     │                │                │    Search      │
     │                │                ├───────────────>│
     │                │                │                │
     │                │                │ 4. Return      │
     │                │                │    Results     │
     │                │                │<───────────────┤
     │                │                │                │
     │                │ 5. Format      │                │
     │                │    Response    │                │
     │                │<───────────────┤                │
     │                │                │                │
     │ 6. Return      │                │                │
     │    to Agent    │                │                │
     │<───────────────┤                │                │
     │                │                │                │
```

---

## 4. File Structure & Responsibilities

```
InfoChatAgent/
│
├── fastapi_server.py          # FastAPI application entry point
│   ├── Routes: /, /{page}, /api/chat, /api/health
│   ├── Agent initialization
│   └── Chat widget injection
│
├── langgraph_agent.py         # LangGraph agent implementation
│   ├── AgentState (TypedDict)
│   ├── TATAMotorsAgent class
│   │   ├── __init__()         # Initialize MCP, create graph
│   │   ├── _create_graph()    # Build LangGraph workflow
│   │   ├── agent_node()       # Decision making node
│   │   ├── tools_node()       # Tool execution node
│   │   ├── should_continue()  # Routing logic
│   │   └── process_query()    # Main entry point
│   └── Helper methods
│
├── mcp_server.py              # MCP Server implementation
│   ├── MCPServer class
│   │   ├── __init__()         # Initialize crawler, tools
│   │   ├── handle_request()   # Route MCP requests
│   │   ├── _list_tools()      # Return available tools
│   │   ├── _call_tool()       # Execute tool
│   │   └── Tool methods:
│   │       ├── search_documents()
│   │       ├── get_vehicle_info()
│   │       ├── get_pricing()
│   │       ├── get_offers()
│   │       └── get_contact_info()
│   └── SimpleCrawler instance
│
├── simple_crawler.py          # Document retrieval system
│   ├── SimpleCrawler class
│   │   ├── __init__()
│   │   ├── crawl_html_pages() # Load HTML files
│   │   ├── search_documents() # Keyword search
│   │   ├── store_documents()  # Store in memory
│   │   └── _get_page_type()   # Categorize pages
│   └── Document storage
│
├── Sample_Html_Car_Sales/     # HTML documents
│   ├── index.html
│   ├── passenger-cars.html
│   ├── nexon-brochure.html
│   ├── chat.html              # Standalone chat UI
│   └── ... (other pages)
│
├── run_agent.py               # Test script
├── requirements.txt           # Dependencies
└── DOCUMENTATION.md           # This file
```

---

## 5. Data Flow Diagram

### 5.1 Complete Request-Response Flow

```
┌─────────┐
│  USER   │
└────┬────┘
     │ "What is the price of Nexon?"
     │
     ▼
┌─────────────────────────────────────┐
│  FASTAPI SERVER                     │
│  POST /api/chat                     │
│  {message: "What is..."}            │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  LANGGRAPH AGENT                    │
│  process_query()                    │
│                                     │
│  Initial State:                     │
│  {                                  │
│    messages: [HumanMessage],        │
│    context: {}                      │
│  }                                  │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  AGENT NODE                         │
│  agent_node(state)                  │
│                                     │
│  1. Extract message                 │
│  2. Check _needs_tools()            │
│     → Keywords: ["price", "nexon"]  │
│     → Result: TRUE                  │
│  3. Generate tool call              │
│     → Tool: "get_pricing"           │
│     → Args: {vehicle_name: "nexon"} │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  TOOLS NODE                         │
│  tools_node(state)                  │
│                                     │
│  1. Extract tool_calls              │
│  2. Build MCP request               │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  MCP SERVER                         │
│  handle_request()                   │
│                                     │
│  Request:                           │
│  {                                  │
│    method: "tools/call",            │
│    params: {                        │
│      name: "get_pricing",           │
│      arguments: {...}               │
│    }                                │
│  }                                  │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  TOOL EXECUTION                     │
│  get_pricing(args)                  │
│                                     │
│  1. Extract vehicle_name            │
│  2. Build search query              │
│  3. Call crawler.search_documents() │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  SIMPLE CRAWLER                     │
│  search_documents(query)            │
│                                     │
│  1. Tokenize query                  │
│  2. Search in documents             │
│  3. Rank by relevance               │
│  4. Return top 5 results            │
└────┬────────────────────────────────┘
     │
     │ Results: [{title, content, ...}]
     │
     ▼
┌─────────────────────────────────────┐
│  MCP SERVER                         │
│  Format response                    │
│                                     │
│  {                                  │
│    content: [{                      │
│      type: "text",                  │
│      text: "Pricing for nexon..."   │
│    }]                               │
│  }                                  │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  TOOLS NODE                         │
│  Format final response              │
│                                     │
│  "Based on TATA Motors information: │
│   [pricing details...]"             │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  LANGGRAPH AGENT                    │
│  Return result                      │
│                                     │
│  result["messages"][-1].content     │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  FASTAPI SERVER                     │
│  Return JSON response               │
│                                     │
│  {                                  │
│    response: "Based on...",         │
│    status: "success"                │
│  }                                  │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────┐
│  USER   │
│ (Browser)│
└─────────┘
```

---

## 6. State Management

### 6.1 AgentState Structure

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: Dict[str, Any]
```

### 6.2 State Transitions

```
Initial State:
{
  messages: [HumanMessage("What is the price of Nexon?")],
  context: {}
}
        │
        ▼
After agent_node:
{
  messages: [
    HumanMessage("What is the price of Nexon?"),
    AIMessage(content="", additional_kwargs={
      tool_calls: [{
        name: "get_pricing",
        arguments: {vehicle_name: "nexon"}
      }]
    })
  ],
  context: {}
}
        │
        ▼
After tools_node:
{
  messages: [
    HumanMessage("What is the price of Nexon?"),
    AIMessage(...tool_calls...),
    AIMessage("Based on TATA Motors information: ...")
  ],
  context: {}
}
```

---

## 7. API Endpoints

### 7.1 Endpoint Documentation

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/` | GET | Main page | - | HTML |
| `/{page}` | GET | HTML pages | page_name | HTML |
| `/api/chat` | POST | Chat with agent | `{message: str}` | `{response: str, status: str}` |
| `/api/health` | GET | Health check | - | `{status: str, agent_ready: bool}` |
| `/api/initialize` | POST | Reinit KB | - | `{status: str, message: str}` |

### 7.2 Example API Calls

```bash
# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the price of Nexon?"}'

# Health
curl http://localhost:8000/api/health
```

---

## 8. Tool Descriptions

### 8.1 Available Tools

| Tool Name | Purpose | Input | Output |
|-----------|---------|-------|--------|
| `search_documents` | General search | `{query: str}` | Top 3 relevant docs |
| `get_vehicle_info` | Vehicle details | `{vehicle_name: str}` | Specs & features |
| `get_pricing` | Price info | `{vehicle_name: str}` | Pricing details |
| `get_offers` | Current offers | `{}` | Promotions |
| `get_contact_info` | Contact details | `{}` | Contact info |

### 8.2 Tool Selection Logic

```
Query Keywords → Tool Mapping:

["price", "cost", "pricing"] → get_pricing
["offer", "discount", "promotion"] → get_offers
["contact", "phone", "email"] → get_contact_info
["nexon", "harrier", "safari", ...] → get_vehicle_info
[other] → search_documents
```

---

## 9. Deployment Guide

### 9.1 Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt
```

### 9.2 Start Application

```bash
# Start server
python fastapi_server.py

# Access
http://localhost:8000          # Main page
http://localhost:8000/chat.html # Chat interface
```

### 9.3 Testing

```bash
# Test agent directly
python run_agent.py

# Test API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

---

## 10. Key Features

### 10.1 LangGraph Integration
- State-based conversation management
- Conditional routing (tools vs direct response)
- Graph compilation for efficient execution

### 10.2 MCP Server
- Standardized tool interface
- Dynamic tool registration
- Request/response formatting

### 10.3 Document Retrieval
- HTML parsing with BeautifulSoup
- Keyword-based search
- Relevance scoring

### 10.4 User Interface
- Modern chat widget
- Typing indicators
- Responsive design
- Smooth animations

---

## 11. Future Enhancements

1. **Vector Database Integration**
   - Replace keyword search with semantic search
   - Use ChromaDB or similar

2. **LLM Integration**
   - Add Ollama for natural language generation
   - Improve response quality

3. **Multi-turn Conversations**
   - Maintain conversation history
   - Context-aware responses

4. **Advanced Tools**
   - Vehicle comparison
   - Test drive booking
   - Dealer locator

---

## 12. Troubleshooting

### Common Issues

**Port 8000 in use:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Agent not responding:**
- Check if server is running
- Verify HTML documents exist
- Check browser console for errors

**Import errors:**
```bash
pip install -r requirements.txt --upgrade
```

---

## 13. Conclusion

This POC demonstrates a complete agentic AI system with:
- ✅ Modular architecture
- ✅ Tool-based extensibility
- ✅ Clean separation of concerns
- ✅ Production-ready API
- ✅ Modern UI/UX

The system can be extended with additional tools, better LLMs, and enhanced retrieval mechanisms for production deployment.

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Author:** AI Development Team
