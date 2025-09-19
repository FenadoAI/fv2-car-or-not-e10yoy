# Tech Stack

## Backend
FastAPI, Python 3.8+, Motor (AsyncIOMotorClient), MongoDB, Pydantic

### AI Agents
Extensible AI agents library with LangChain and MCP support for building intelligent services. See [AI Agents Documentation](./aiagent.md) for detailed implementation guide.

### Installed Packages
fastapi==0.110.1, uvicorn==0.25.0, motor==3.3.1, pymongo==4.5.0, pydantic>=2.6.4, email-validator>=2.2.0, python-jose>=3.3.0, passlib>=1.7.4, pyjwt>=2.10.1, python-dotenv>=1.0.1, requests>=2.31.0, cryptography>=42.0.8, bcrypt

### API Structure Pattern
```python
from fastapi import FastAPI, APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import os, uuid
from datetime import datetime

# Setup
app = FastAPI()
api_router = APIRouter(prefix="/api")
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

# Model
class Item(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Route
@api_router.post("/items", response_model=Item)
async def create_item(data: ItemCreate):
    item = Item(**data.dict())
    await db.items.insert_one(item.dict())
    return item

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentication Pattern
```python
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

## Frontend
React 19, React Router v7, Tailwind CSS, shadcn/ui components, craco

### Installed Packages
react@19, react-dom@19, react-router-dom@7, axios@1, tailwindcss@3, @radix-ui/*, lucide-react, react-hook-form@7, zod@3, clsx, tailwind-merge

### Component Pattern
```javascript
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

export function MyComponent() {
  const [data, setData] = useState([])
  
  useEffect(() => {
    axios.get(`${API_URL}/api/items`)
      .then(res => setData(res.data))
      .catch(err => console.error(err))
  }, [])
  
  return (
    <Card>
      {data.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
    </Card>
  )
}
```

## Test Pattern
```python
import requests
import json
from datetime import datetime

API_BASE = "https://your-backend-url.com/api"  # Replace with your actual backend API URL

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def test_create_item(self):
        payload = {"name": "Test Item"}
        response = self.session.post(f"{API_BASE}/items", json=payload)
        
        if response.status_code == 200:
            self.log_test("Create Item", True, f"Created: {response.json()}")
            return True
        else:
            self.log_test("Create Item", False, f"Status: {response.status_code}")
            return False
    
    def run_all_tests(self):
        print("🚀 Starting API Tests")
        self.test_create_item()
        # Add more tests

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_all_tests()
```

## Database
MongoDB, collections: users, items, status_checks

## Environment Variables
MONGO_URL, DB_NAME, JWT_SECRET_KEY, CORS_ORIGINS

## Run Commands
Backend: `uvicorn server:app --reload`
Frontend: `bun start`
Tests: `cd backend && python tests/test_agents.py` - See [HOW_TO_TEST.md](../HOW_TO_TEST.md) for testing patterns
