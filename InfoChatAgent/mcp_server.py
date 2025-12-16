import json
from typing import Dict, Any, List
import asyncio
from web_crawler import WebCrawler

class MCPServer:
    def __init__(self):
        self.crawler = WebCrawler()
        self.tools = {
            "search_documents": self.search_documents,
            "get_vehicle_info": self.get_vehicle_info,
            "get_pricing": self.get_pricing,
            "get_offers": self.get_offers,
            "get_contact_info": self.get_contact_info
        }
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "tools/list":
            return self._list_tools()
        elif method == "tools/call":
            return await self._call_tool(params)
        else:
            return {"error": f"Unknown method: {method}"}
    
    def _list_tools(self) -> Dict[str, Any]:
        return {
            "tools": [
                {
                    "name": "search_documents",
                    "description": "Search through TATA Motors documents and brochures",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_vehicle_info",
                    "description": "Get detailed information about TATA vehicles",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "vehicle_name": {"type": "string", "description": "Name of the vehicle"}
                        },
                        "required": ["vehicle_name"]
                    }
                },
                {
                    "name": "get_pricing",
                    "description": "Get pricing information for TATA vehicles",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "vehicle_name": {"type": "string", "description": "Name of the vehicle"}
                        }
                    }
                },
                {
                    "name": "get_offers",
                    "description": "Get current offers and promotions",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "get_contact_info",
                    "description": "Get contact information and dealer details",
                    "inputSchema": {"type": "object", "properties": {}}
                }
            ]
        }
    
    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name in self.tools:
            try:
                result = await self.tools[tool_name](arguments)
                return {"content": [{"type": "text", "text": result}]}
            except Exception as e:
                return {"error": f"Tool execution failed: {str(e)}"}
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    async def search_documents(self, args: Dict[str, Any]) -> str:
        query = args.get("query", "")
        results = self.crawler.search_documents(query)
        
        if not results:
            return "No relevant documents found."
        
        response = f"Found {len(results)} relevant documents:\n\n"
        for i, result in enumerate(results[:3], 1):
            response += f"{i}. {result['metadata']['title']}\n"
            response += f"   {result['content'][:200]}...\n\n"
        
        return response
    
    async def get_vehicle_info(self, args: Dict[str, Any]) -> str:
        vehicle_name = args.get("vehicle_name", "").lower()
        query = f"{vehicle_name} specifications features"
        results = self.crawler.search_documents(query)
        
        if results:
            return f"Information about {vehicle_name}:\n{results[0]['content']}"
        return f"No information found for {vehicle_name}"
    
    async def get_pricing(self, args: Dict[str, Any]) -> str:
        vehicle_name = args.get("vehicle_name", "")
        query = f"{vehicle_name} price pricing cost"
        results = self.crawler.search_documents(query)
        
        if results:
            return f"Pricing for {vehicle_name}:\n{results[0]['content']}"
        return "Pricing information not available"
    
    async def get_offers(self, args: Dict[str, Any]) -> str:
        results = self.crawler.search_documents("offers promotions discounts")
        
        if results:
            return f"Current offers:\n{results[0]['content']}"
        return "No current offers available"
    
    async def get_contact_info(self, args: Dict[str, Any]) -> str:
        results = self.crawler.search_documents("contact phone email address")
        
        if results:
            return f"Contact information:\n{results[0]['content']}"
        return "Contact information not available"