from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

# AI agents
from ai_agents.agents import AgentConfig, SearchAgent, ChatAgent


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AI agents init
agent_config = AgentConfig()
search_agent: Optional[SearchAgent] = None
chat_agent: Optional[ChatAgent] = None

# Main app
app = FastAPI(title="AI Agents API", description="Minimal AI Agents API with LangGraph and MCP support")

# API router
api_router = APIRouter(prefix="/api")


# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# Car rating models
class Car(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    make: str
    model: str
    year: int
    image_url: str
    hot_votes: int = 0
    not_votes: int = 0
    total_votes: int = 0
    hot_percentage: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CarCreate(BaseModel):
    make: str
    model: str
    year: int
    image_url: str

class CarResponse(BaseModel):
    id: str
    make: str
    model: str
    year: int
    image_url: str
    hot_votes: int
    not_votes: int
    total_votes: int
    hot_percentage: float

class VoteRequest(BaseModel):
    car_id: str
    vote_type: str  # "hot" or "not"

class VoteResponse(BaseModel):
    success: bool
    car: CarResponse
    message: str

# AI agent models
class ChatRequest(BaseModel):
    message: str
    agent_type: str = "chat"  # "chat" or "search"
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_type: str
    capabilities: List[str]
    metadata: dict = Field(default_factory=dict)
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class SearchResponse(BaseModel):
    success: bool
    query: str
    summary: str
    search_results: Optional[dict] = None
    sources_count: int
    error: Optional[str] = None

# Routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Car rating routes
@api_router.get("/cars/random", response_model=CarResponse)
async def get_random_car():
    """Get a random car for rating"""
    try:
        # Get a random car from the database
        pipeline = [{"$sample": {"size": 1}}]
        cars = await db.cars.aggregate(pipeline).to_list(1)

        if not cars:
            raise HTTPException(status_code=404, detail="No cars found in database")

        car = cars[0]
        return CarResponse(
            id=car["id"],
            make=car["make"],
            model=car["model"],
            year=car["year"],
            image_url=car["image_url"],
            hot_votes=car["hot_votes"],
            not_votes=car["not_votes"],
            total_votes=car["total_votes"],
            hot_percentage=car["hot_percentage"]
        )

    except Exception as e:
        logger.error(f"Error getting random car: {e}")
        raise HTTPException(status_code=500, detail="Failed to get random car")

@api_router.post("/cars/{car_id}/vote", response_model=VoteResponse)
async def vote_for_car(car_id: str, vote_request: VoteRequest):
    """Vote for a car as 'hot' or 'not'"""
    try:
        if vote_request.vote_type not in ["hot", "not"]:
            raise HTTPException(status_code=400, detail="Vote type must be 'hot' or 'not'")

        # Find the car
        car = await db.cars.find_one({"id": car_id})
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")

        # Update vote counts
        if vote_request.vote_type == "hot":
            new_hot_votes = car["hot_votes"] + 1
            new_not_votes = car["not_votes"]
        else:
            new_hot_votes = car["hot_votes"]
            new_not_votes = car["not_votes"] + 1

        new_total_votes = new_hot_votes + new_not_votes
        new_hot_percentage = (new_hot_votes / new_total_votes * 100) if new_total_votes > 0 else 0

        # Update the car in database
        await db.cars.update_one(
            {"id": car_id},
            {
                "$set": {
                    "hot_votes": new_hot_votes,
                    "not_votes": new_not_votes,
                    "total_votes": new_total_votes,
                    "hot_percentage": round(new_hot_percentage, 1)
                }
            }
        )

        # Return updated car data
        updated_car = CarResponse(
            id=car["id"],
            make=car["make"],
            model=car["model"],
            year=car["year"],
            image_url=car["image_url"],
            hot_votes=new_hot_votes,
            not_votes=new_not_votes,
            total_votes=new_total_votes,
            hot_percentage=round(new_hot_percentage, 1)
        )

        return VoteResponse(
            success=True,
            car=updated_car,
            message=f"Vote recorded! This car is {updated_car.hot_percentage}% hot."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error voting for car: {e}")
        raise HTTPException(status_code=500, detail="Failed to record vote")

@api_router.post("/cars", response_model=CarResponse)
async def create_car(car_data: CarCreate):
    """Add a new car to the database"""
    try:
        car_dict = car_data.dict()
        car_obj = Car(**car_dict)

        # Insert into database
        await db.cars.insert_one(car_obj.dict())

        return CarResponse(
            id=car_obj.id,
            make=car_obj.make,
            model=car_obj.model,
            year=car_obj.year,
            image_url=car_obj.image_url,
            hot_votes=car_obj.hot_votes,
            not_votes=car_obj.not_votes,
            total_votes=car_obj.total_votes,
            hot_percentage=car_obj.hot_percentage
        )

    except Exception as e:
        logger.error(f"Error creating car: {e}")
        raise HTTPException(status_code=500, detail="Failed to create car")

@api_router.post("/cars/initialize")
async def initialize_cars():
    """Initialize the database with sample car data"""
    try:
        # Check if cars already exist
        existing_count = await db.cars.count_documents({})
        if existing_count > 0:
            return {"message": f"Database already has {existing_count} cars", "initialized": False}

        # Sample car data with high-quality Unsplash images
        sample_cars = [
            {
                "make": "Ferrari",
                "model": "488 GTB",
                "year": 2020,
                "image_url": "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "Lamborghini",
                "model": "Huracan",
                "year": 2021,
                "image_url": "https://images.unsplash.com/photo-1563720223185-11003d516935?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "Porsche",
                "model": "911 GT3",
                "year": 2022,
                "image_url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "McLaren",
                "model": "720S",
                "year": 2020,
                "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "Bugatti",
                "model": "Chiron",
                "year": 2021,
                "image_url": "https://images.unsplash.com/photo-1525609004556-c46c7d6cf023?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "Aston Martin",
                "model": "DBS Superleggera",
                "year": 2020,
                "image_url": "https://images.unsplash.com/photo-1570618834314-ec2ec95d4d7c?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "BMW",
                "model": "M4",
                "year": 2021,
                "image_url": "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "Mercedes",
                "model": "AMG GT",
                "year": 2020,
                "image_url": "https://images.unsplash.com/photo-1563707346-8d5c8dd7e63a?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "Audi",
                "model": "R8",
                "year": 2021,
                "image_url": "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "Tesla",
                "model": "Model S Plaid",
                "year": 2022,
                "image_url": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "Chevrolet",
                "model": "Corvette C8",
                "year": 2021,
                "image_url": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&h=450&fit=crop&crop=center"
            },
            {
                "make": "Ford",
                "model": "Mustang Shelby GT500",
                "year": 2020,
                "image_url": "https://images.unsplash.com/photo-1494976688153-d4c7c48bbcdb?w=800&h=450&fit=crop&crop=center"
            }
        ]

        # Create Car objects and insert into database
        cars_to_insert = []
        for car_data in sample_cars:
            car_obj = Car(**car_data)
            cars_to_insert.append(car_obj.dict())

        # Bulk insert
        result = await db.cars.insert_many(cars_to_insert)

        return {
            "message": f"Successfully initialized {len(result.inserted_ids)} cars",
            "initialized": True,
            "car_count": len(result.inserted_ids)
        }

    except Exception as e:
        logger.error(f"Error initializing cars: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize cars")


# AI agent routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    # Chat with AI agent
    global search_agent, chat_agent
    
    try:
        # Init agents if needed
        if request.agent_type == "search" and search_agent is None:
            search_agent = SearchAgent(agent_config)
            
        elif request.agent_type == "chat" and chat_agent is None:
            chat_agent = ChatAgent(agent_config)
        
        # Select agent
        agent = search_agent if request.agent_type == "search" else chat_agent
        
        if agent is None:
            raise HTTPException(status_code=500, detail="Failed to initialize agent")
        
        # Execute agent
        response = await agent.execute(request.message)
        
        return ChatResponse(
            success=response.success,
            response=response.content,
            agent_type=request.agent_type,
            capabilities=agent.get_capabilities(),
            metadata=response.metadata,
            error=response.error
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            success=False,
            response="",
            agent_type=request.agent_type,
            capabilities=[],
            error=str(e)
        )


@api_router.post("/search", response_model=SearchResponse)
async def search_and_summarize(request: SearchRequest):
    # Web search with AI summary
    global search_agent
    
    try:
        # Init search agent if needed
        if search_agent is None:
            search_agent = SearchAgent(agent_config)
        
        # Search with agent
        search_prompt = f"Search for information about: {request.query}. Provide a comprehensive summary with key findings."
        result = await search_agent.execute(search_prompt, use_tools=True)
        
        if result.success:
            return SearchResponse(
                success=True,
                query=request.query,
                summary=result.content,
                search_results=result.metadata,
                sources_count=result.metadata.get("tools_used", 0)
            )
        else:
            return SearchResponse(
                success=False,
                query=request.query,
                summary="",
                sources_count=0,
                error=result.error
            )
            
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return SearchResponse(
            success=False,
            query=request.query,
            summary="",
            sources_count=0,
            error=str(e)
        )


@api_router.get("/agents/capabilities")
async def get_agent_capabilities():
    # Get agent capabilities
    try:
        capabilities = {
            "search_agent": SearchAgent(agent_config).get_capabilities(),
            "chat_agent": ChatAgent(agent_config).get_capabilities()
        }
        return {
            "success": True,
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Initialize agents on startup
    global search_agent, chat_agent
    logger.info("Starting AI Agents API...")
    
    # Lazy agent init for faster startup
    logger.info("AI Agents API ready!")


@app.on_event("shutdown")
async def shutdown_db_client():
    # Cleanup on shutdown
    global search_agent, chat_agent
    
    # Close MCP
    if search_agent and search_agent.mcp_client:
        # MCP cleanup automatic
        pass
    
    client.close()
    logger.info("AI Agents API shutdown complete.")
