import asyncio
from langgraph_agent import TATAMotorsAgent

async def main():
    print("Starting TATA Motors LangGraph Agent...")
    print("="*60)
    
    try:
        agent = TATAMotorsAgent()
        print("\nAgent initialized successfully!")
        print("="*60)
        
        # Test query
        query = "What is the price of Nexon?"
        print(f"\nTest Query: {query}")
        print("-"*60)
        
        response = await agent.process_query(query)
        print(f"\nResponse:\n{response}")
        print("="*60)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
