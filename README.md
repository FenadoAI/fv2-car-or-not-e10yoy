# Project Setup

## Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload
```

## Frontend  
```bash
cd frontend
bun install
bun start
```

## Environment
Backend: Create `.env` with `MONGO_URL`, `DB_NAME`, `JWT_SECRET_KEY`  
Frontend: Uses `REACT_APP_API_URL` (defaults to http://localhost:8000)

### Frontend Environment Variables
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)
- For production: Set to your deployed backend URL (e.g., https://api.yourdomain.com)

## Test
```bash
# Test AI agents
cd backend && python tests/test_agents.py

# Test backend API (if server is running)
cd backend && python tests/test_api.py
```
