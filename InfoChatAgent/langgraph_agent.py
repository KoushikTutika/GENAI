from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import TypedDict, Annotated, Sequence, Dict, Any
import operator
from mcp_server import MCPServer

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: Dict[str, Any]

class TATAMotorsAgent:
    def __init__(self):
        self.mcp_server = MCPServer()
        
        # Initialize and crawl documents
        self._initialize_knowledge_base()
        
        # Create the graph
        self.graph = self._create_graph()
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base by crawling HTML documents"""
        documents = self.mcp_server.crawler.crawl_html_pages()
        self.mcp_server.crawler.store_documents(documents)
        print(f"Initialized knowledge base with {len(documents)} documents")
    
    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self.agent_node)
        workflow.add_node("tools", self.tools_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        workflow.add_edge("tools", END)
        
        return workflow.compile()
    
    async def agent_node(self, state: AgentState) -> Dict[str, Any]:
        messages = state["messages"]
        
        # Get the last human message
        last_message = messages[-1].content if messages else ""
        
        # Create system prompt
        system_prompt = """You are a TATA Motors customer service agent. You help customers with:
        - Vehicle information and specifications
        - Pricing and offers
        - Brochures and documentation
        - Contact information
        - Test drive bookings
        
        Use the available tools to search for accurate information from TATA Motors documents.
        Be helpful, professional, and provide detailed responses."""
        
        # Determine if we need to use tools
        if self._needs_tools(last_message):
            # Generate tool calls
            tool_call = self._generate_tool_call(last_message)
            return {
                "messages": [AIMessage(content="", additional_kwargs={"tool_calls": [tool_call]})]
            }
        else:
            # Generate simple response without Ollama
            response = f"I can help you with information about TATA Motors vehicles. Your query: '{last_message}'. Please ask about specific vehicles, pricing, offers, or contact information."
            
            return {
                "messages": [AIMessage(content=response)]
            }
    
    async def tools_node(self, state: AgentState) -> Dict[str, Any]:
        messages = state["messages"]
        last_message = messages[-1]
        
        # Extract tool calls from the last message
        tool_calls = last_message.additional_kwargs.get("tool_calls", [])
        
        results = []
        for tool_call in tool_calls:
            # Execute tool via MCP server
            mcp_request = {
                "method": "tools/call",
                "params": {
                    "name": tool_call["name"],
                    "arguments": tool_call["arguments"]
                }
            }
            
            result = await self.mcp_server.handle_request(mcp_request)
            tool_result = result.get("content", [{}])[0].get("text", "No result")
            results.append(tool_result)
        
        # Generate final response with tool results
        context = "\n".join(results)
        user_query = state["messages"][-2].content if len(state["messages"]) > 1 else ""
        
        response_text = f"Based on TATA Motors information:\n\n{context}"
        
        return {
            "messages": [AIMessage(content=response_text)]
        }
    
    def should_continue(self, state: AgentState) -> str:
        messages = state["messages"]
        last_message = messages[-1]
        
        # Check if the last message has tool calls
        if hasattr(last_message, 'additional_kwargs') and last_message.additional_kwargs.get("tool_calls"):
            return "continue"
        return "end"
    
    def _needs_tools(self, message: str) -> bool:
        """Determine if the message requires tool usage"""
        tool_keywords = [
            "price", "cost", "specification", "feature", "offer", "discount",
            "contact", "phone", "email", "brochure", "nexon", "harrier",
            "safari", "punch", "altroz", "tiago", "electric", "ev"
        ]
        return any(keyword in message.lower() for keyword in tool_keywords)
    
    def _generate_tool_call(self, message: str) -> Dict[str, Any]:
        """Generate appropriate tool call based on message content"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["price", "cost", "pricing"]):
            vehicle = self._extract_vehicle_name(message)
            return {
                "name": "get_pricing",
                "arguments": {"vehicle_name": vehicle}
            }
        elif any(word in message_lower for word in ["offer", "discount", "promotion"]):
            return {
                "name": "get_offers",
                "arguments": {}
            }
        elif any(word in message_lower for word in ["contact", "phone", "email"]):
            return {
                "name": "get_contact_info",
                "arguments": {}
            }
        elif any(word in message_lower for word in ["nexon", "harrier", "safari", "punch", "altroz", "tiago"]):
            vehicle = self._extract_vehicle_name(message)
            return {
                "name": "get_vehicle_info",
                "arguments": {"vehicle_name": vehicle}
            }
        else:
            return {
                "name": "search_documents",
                "arguments": {"query": message}
            }
    
    def _extract_vehicle_name(self, message: str) -> str:
        """Extract vehicle name from message"""
        vehicles = ["nexon", "harrier", "safari", "punch", "altroz", "tiago"]
        for vehicle in vehicles:
            if vehicle in message.lower():
                return vehicle
        return ""
    
    async def process_query(self, query: str) -> str:
        """Process a user query and return response"""
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "context": {}
        }
        
        result = await self.graph.ainvoke(initial_state, {"recursion_limit": 100})
        return result["messages"][-1].content