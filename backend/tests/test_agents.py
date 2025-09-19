# Test extensible AI agents library

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load env from backend
load_dotenv(backend_dir / ".env")

async def test_search_agent():
    # Test AI agents with web search
    print("🧪 AI Agents Library Test")
    print("=" * 30)
    
    # Set model name
    os.environ['AI_MODEL_NAME'] = 'gemini-2.5-pro'
    
    try:
        from ai_agents import SearchAgent, AgentConfig
        
        config = AgentConfig()
        print(f"LiteLLM Token: {config.api_key[:10]}...")
        print(f"Model: {config.model_name}")
        print(f"LiteLLM Base URL: {config.api_base_url}")
        
        search_agent = SearchAgent(config)
        print(f"MCP Client: {search_agent.mcp_client is not None}")
        
        if search_agent.mcp_client is None:
            print("❌ No MCP client - web search won't work")
            return False
        
        print("\n🌍 Question: What is the capital of France?")
        print("Searching...")
        
        response = await search_agent.execute(
            "What is the capital of France?", 
            use_tools=True
        )
        
        print(f"\n✅ Success: {response.success}")
        if response.success:
            print(f"📝 Response: {response.content}")
            
            # Check Paris mentioned
            if "Paris" in response.content or "paris" in response.content.lower():
                print("🎯 CORRECT: Response mentions Paris!")
                return True
            else:
                print("⚠️  Response doesn't mention Paris")
                return False
        else:
            print(f"❌ Error: {response.error}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_search_agent())
    if success:
        print("\n🎉 AI Agents Library is working!")
        print("✅ Extensible agents can search the web and provide accurate answers")
        print("💡 You can now extend BaseAgent to create custom AI agents")
    else:
        print("\n❌ AI agents test failed")
        print("🔧 Check your MCP_AUTH_TOKEN and internet connection")
