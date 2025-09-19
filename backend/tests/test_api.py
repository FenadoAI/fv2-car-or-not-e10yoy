# FastAPI server endpoint tests

import requests
import json
import time
import sys
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def test_server_endpoints():
    # Test FastAPI endpoints
    base_url = "http://localhost:8000/api"
    
    print("🌐 Testing FastAPI Server Endpoints")
    print("=" * 40)
    
    # Root endpoint test
    print("1️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["message"] == "Hello World", f"Unexpected message: {data}"
        print("✅ Root endpoint working")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Chat endpoint test
    print("\n2️⃣ Testing chat endpoint...")
    try:
        payload = {
            "message": "What is 2+2?",
            "agent_type": "chat"
        }
        
        response = requests.post(f"{base_url}/chat", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["success"] is True, f"Chat failed: {data.get('error')}"
        assert "4" in data["response"], f"Wrong answer: {data['response']}"
        assert data["agent_type"] == "chat"
        assert "conversation" in data["capabilities"]
        
        print("✅ Chat endpoint working")
        print(f"   Response: {data['response'][:100]}...")
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")
        return False
    
    # Search endpoint test  
    print("\n3️⃣ Testing search endpoint...")
    try:
        payload = {
            "query": "capital of Japan",
            "max_results": 3
        }
        
        response = requests.post(f"{base_url}/search", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["success"] is True, f"Search failed: {data.get('error')}"
        assert "Tokyo" in data["summary"], f"Wrong answer: {data['summary']}"
        assert data["query"] == "capital of Japan"
        
        print("✅ Search endpoint working")
        print(f"   Summary: {data['summary'][:100]}...")
    except Exception as e:
        print(f"❌ Search endpoint failed: {e}")
        return False
    
    # Capabilities endpoint test
    print("\n4️⃣ Testing capabilities endpoint...")
    try:
        response = requests.get(f"{base_url}/agents/capabilities")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["success"] is True, f"Capabilities failed: {data.get('error')}"
        assert "search_agent" in data["capabilities"]
        assert "chat_agent" in data["capabilities"]
        assert "mcp_enabled" in data["capabilities"]["search_agent"]
        
        print("✅ Capabilities endpoint working")
        print(f"   Search agent: {data['capabilities']['search_agent']}")
        print(f"   Chat agent: {data['capabilities']['chat_agent']}")
    except Exception as e:
        print(f"❌ Capabilities endpoint failed: {e}")
        return False
    
    return True


def check_server_running():
    # Check if server running
    try:
        response = requests.get("http://localhost:8000/api/", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    # Main test function
    print("🧪 FastAPI Server Test")
    print("=" * 25)
    
    # Server status check
    if not check_server_running():
        print("❌ Server not running on http://localhost:8000")
        print("💡 Start the server first:")
        print("   cd backend && uvicorn server:app --reload")
        return False
    
    print("✅ Server is running")
    
    # Run tests
    success = test_server_endpoints()
    
    if success:
        print("\n🎉 All API endpoints working!")
        print("✅ FastAPI server with AI agents is fully functional")
    else:
        print("\n❌ Some API tests failed")
        print("🔧 Check server logs for details")
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
