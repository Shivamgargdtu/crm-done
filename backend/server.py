from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from bson import ObjectId

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Create the main app
app = FastAPI(title="Wed Us CRM API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============== HELPER FUNCTIONS ==============

def get_jwt_secret() -> str:
    return os.environ["JWT_SECRET"]

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access"
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh"
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if key == "_id":
            result["id"] = str(value)
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, list):
            result[key] = [serialize_doc(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        else:
            result[key] = value
    return result

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return serialize_doc(user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_admin(request: Request) -> dict:
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ============== PYDANTIC MODELS ==============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "team_member"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    color: Optional[str] = None
    created_at: Optional[str] = None

class TeamMemberCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    color: Optional[str] = None

class LeadCreate(BaseModel):
    companyName: str
    phone: Optional[str] = None
    phone2: Optional[str] = None
    whatsapp: Optional[str] = None
    whatsapp2: Optional[str] = None
    primaryWhatsapp: Optional[int] = 1
    instagram: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    status: Optional[str] = "active"
    category: Optional[str] = "Needs Review"
    priority: Optional[str] = "Medium"
    pipelineStage: Optional[str] = "New Contact"
    assignedTo: Optional[str] = None
    sourceSheet: Optional[str] = None
    nextFollowupDate: Optional[str] = None
    lastContactDate: Optional[str] = None
    portfolioSent: Optional[bool] = False
    priceListSent: Optional[bool] = False
    waSent: Optional[bool] = False
    notes: Optional[str] = None

class LeadUpdate(BaseModel):
    companyName: Optional[str] = None
    phone: Optional[str] = None
    phone2: Optional[str] = None
    whatsapp: Optional[str] = None
    whatsapp2: Optional[str] = None
    primaryWhatsapp: Optional[int] = None
    instagram: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    pipelineStage: Optional[str] = None
    assignedTo: Optional[str] = None
    sourceSheet: Optional[str] = None
    nextFollowupDate: Optional[str] = None
    lastContactDate: Optional[str] = None
    portfolioSent: Optional[bool] = None
    priceListSent: Optional[bool] = None
    waSent: Optional[bool] = None
    notes: Optional[str] = None

class ResponseHistoryEntry(BaseModel):
    response: str
    notes: Optional[str] = None
    timestamp: Optional[str] = None
    teamMember: Optional[str] = None
    duration: Optional[int] = None
    waNumberUsed: Optional[int] = None
    portfolioSent: Optional[bool] = False
    priceListSent: Optional[bool] = False
    waSent: Optional[bool] = False
    nextFollowupDate: Optional[str] = None

# ============== CATEGORY/PRIORITY MAPPINGS ==============

CATEGORY_RANK = {
    "Meeting Done": 1,
    "Interested": 2,
    "Call Back": 3,
    "Busy": 4,
    "No Response": 5,
    "Foreign": 6,
    "Future Projection": 7,
    "Needs Review": 8,
    "Not Interested": 9
}

PRIORITY_RANK = {
    "Highest": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4,
    "Review": 5,
    "Archive": 6
}

RESPONSE_RANK = {
    "Interested": 1,
    "Call Back": 2,
    "Meeting Done": 3,
    "Busy": 4,
    "No Response": 5,
    "Not Interested": 6,
    "Other": 7
}

PIPELINE_STAGES = [
    "New Contact", "Interested", "Send Portfolio", "Time Given",
    "Meeting Scheduled", "Meeting Done", "Project Follow-up", "Onboarded",
    "Unknown", "Call Again 1", "Call Again 2", "Call Again 3",
    "Not Answering", "Not Interested"
]

TEAM_COLORS = ["#E8536A", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#06B6D4"]

# ============== AUTH ROUTES ==============

@api_router.post("/auth/login")
async def login(credentials: UserLogin, response: Response):
    email = credentials.email.lower()
    user = await db.users.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id = str(user["_id"])
    access_token = create_access_token(user_id, email, user["role"])
    refresh_token = create_refresh_token(user_id)
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=900, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    
    user_data = serialize_doc(user)
    user_data.pop("password_hash", None)
    return user_data

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out successfully"}

@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    user.pop("password_hash", None)
    return user

@api_router.post("/auth/refresh")
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        user_id = str(user["_id"])
        access_token = create_access_token(user_id, user["email"], user["role"])
        
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=900, path="/")
        
        return {"message": "Token refreshed"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# ============== TEAM ROUTES ==============

@api_router.get("/team")
async def get_team_members(request: Request):
    await get_current_user(request)
    members = await db.users.find({}, {"password_hash": 0}).to_list(100)
    return [serialize_doc(m) for m in members]

@api_router.post("/team")
async def create_team_member(member: TeamMemberCreate, request: Request):
    await require_admin(request)
    
    existing = await db.users.find_one({"email": member.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Assign color if not provided
    count = await db.users.count_documents({})
    color = member.color or TEAM_COLORS[count % len(TEAM_COLORS)]
    
    user_doc = {
        "email": member.email.lower(),
        "password_hash": hash_password(member.password),
        "name": member.name,
        "role": "team_member",
        "color": color,
        "created_at": datetime.now(timezone.utc)
    }
    
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    user_data = serialize_doc(user_doc)
    user_data.pop("password_hash", None)
    return user_data

@api_router.delete("/team/{user_id}")
async def delete_team_member(user_id: str, request: Request):
    await require_admin(request)
    
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Team member deleted"}

# ============== LEADS ROUTES ==============

def calculate_ranks(lead_data: dict) -> dict:
    """Calculate and add rank fields based on category, priority, and response"""
    if "category" in lead_data and lead_data["category"]:
        lead_data["categoryRank"] = CATEGORY_RANK.get(lead_data["category"], 99)
    if "priority" in lead_data and lead_data["priority"]:
        lead_data["priorityRank"] = PRIORITY_RANK.get(lead_data["priority"], 99)
    return lead_data

def calculate_most_common_response(response_history: list) -> tuple:
    """Calculate most common response from history"""
    if not response_history:
        return None, None
    
    response_counts = {}
    for entry in response_history:
        resp = entry.get("response", "Other")
        response_counts[resp] = response_counts.get(resp, 0) + 1
    
    most_common = max(response_counts, key=response_counts.get)
    rank = RESPONSE_RANK.get(most_common, 7)
    return most_common, rank

@api_router.get("/leads")
async def get_leads(
    request: Request,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    pipelineStage: Optional[str] = None,
    assignedTo: Optional[str] = None,
    search: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
):
    user = await get_current_user(request)
    
    query = {}
    
    # Team members can only see their assigned leads
    if user["role"] == "team_member":
        query["assignedTo"] = user["id"]
    elif assignedTo:
        query["assignedTo"] = assignedTo
    
    if category:
        query["category"] = category
    if priority:
        query["priority"] = priority
    if pipelineStage:
        query["pipelineStage"] = pipelineStage
    if source == "instagram":
        query["instagram"] = {"$exists": True, "$ne": None, "$ne": ""}
    if source == "whatsapp":
        query["$or"] = [
            {"whatsapp": {"$exists": True, "$ne": None, "$ne": ""}},
            {"whatsapp2": {"$exists": True, "$ne": None, "$ne": ""}}
        ]
    if search:
        query["$or"] = [
            {"companyName": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"city": {"$regex": search, "$options": "i"}}
        ]
    
    leads = await db.leads.find(query, {"_id": 1, "companyName": 1, "phone": 1, "email": 1, "city": 1, "state": 1, "category": 1, "categoryRank": 1, "priority": 1, "priorityRank": 1, "pipelineStage": 1, "assignedTo": 1, "nextFollowupDate": 1, "lastContactDate": 1, "dateAdded": 1, "instagram": 1, "whatsapp": 1, "callCount": 1, "mostCommonResponse": 1}).sort([("categoryRank", 1), ("priorityRank", 1)]).skip(skip).limit(limit).to_list(limit)
    
    return [serialize_doc(lead) for lead in leads]

@api_router.get("/leads/count")
async def get_leads_count(request: Request):
    user = await get_current_user(request)
    
    base_query = {}
    if user["role"] == "team_member":
        base_query["assignedTo"] = user["id"]
    
    # Get today's date range
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    week_end = today + timedelta(days=7)
    
    counts = {
        "total": await db.leads.count_documents(base_query),
        "today": await db.leads.count_documents({**base_query, "nextFollowupDate": {"$gte": today.isoformat(), "$lt": tomorrow.isoformat()}}),
        "tomorrow": await db.leads.count_documents({**base_query, "nextFollowupDate": {"$gte": tomorrow.isoformat(), "$lt": (tomorrow + timedelta(days=1)).isoformat()}}),
        "thisWeek": await db.leads.count_documents({**base_query, "nextFollowupDate": {"$gte": today.isoformat(), "$lt": week_end.isoformat()}}),
        "meetingDone": await db.leads.count_documents({**base_query, "category": "Meeting Done"}),
        "interested": await db.leads.count_documents({**base_query, "category": "Interested"}),
        "callBack": await db.leads.count_documents({**base_query, "category": "Call Back"}),
        "busy": await db.leads.count_documents({**base_query, "category": "Busy"}),
        "noResponse": await db.leads.count_documents({**base_query, "category": "No Response"}),
        "foreign": await db.leads.count_documents({**base_query, "category": "Foreign"}),
        "futureProjection": await db.leads.count_documents({**base_query, "category": "Future Projection"}),
        "needsReview": await db.leads.count_documents({**base_query, "category": "Needs Review"}),
        "notInterested": await db.leads.count_documents({**base_query, "category": "Not Interested"}),
        "instagram": await db.leads.count_documents({**base_query, "instagram": {"$exists": True, "$ne": None, "$ne": ""}}),
        "whatsapp": await db.leads.count_documents({**base_query, "$or": [{"whatsapp": {"$exists": True, "$ne": None, "$ne": ""}}, {"whatsapp2": {"$exists": True, "$ne": None, "$ne": ""}}]})
    }
    
    return counts

@api_router.get("/leads/{lead_id}")
async def get_lead(lead_id: str, request: Request):
    user = await get_current_user(request)
    
    lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check access
    if user["role"] == "team_member" and lead.get("assignedTo") != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return serialize_doc(lead)

@api_router.post("/leads")
async def create_lead(lead: LeadCreate, request: Request):
    user = await get_current_user(request)
    
    lead_data = lead.model_dump()
    lead_data = calculate_ranks(lead_data)
    lead_data["dateAdded"] = datetime.now(timezone.utc).isoformat()
    lead_data["responseHistory"] = []
    lead_data["callCount"] = 0
    lead_data["isDuplicate"] = False
    lead_data["duplicateDismissed"] = False
    lead_data["mostCommonResponse"] = None
    lead_data["mostCommonResponseRank"] = None
    
    result = await db.leads.insert_one(lead_data)
    lead_data["_id"] = result.inserted_id
    
    return serialize_doc(lead_data)

@api_router.put("/leads/{lead_id}")
async def update_lead(lead_id: str, lead_update: LeadUpdate, request: Request):
    user = await get_current_user(request)
    
    lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check access
    if user["role"] == "team_member" and lead.get("assignedTo") != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = {k: v for k, v in lead_update.model_dump().items() if v is not None}
    update_data = calculate_ranks(update_data)
    
    await db.leads.update_one({"_id": ObjectId(lead_id)}, {"$set": update_data})
    
    updated_lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
    return serialize_doc(updated_lead)

@api_router.post("/leads/{lead_id}/response")
async def add_response_history(lead_id: str, entry: ResponseHistoryEntry, request: Request):
    user = await get_current_user(request)
    
    lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check access
    if user["role"] == "team_member" and lead.get("assignedTo") != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    entry_data = entry.model_dump()
    entry_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    entry_data["teamMember"] = user["id"]
    
    # Update response history and recalculate most common response
    response_history = lead.get("responseHistory", [])
    response_history.append(entry_data)
    
    most_common, rank = calculate_most_common_response(response_history)
    
    await db.leads.update_one(
        {"_id": ObjectId(lead_id)},
        {
            "$push": {"responseHistory": entry_data},
            "$inc": {"callCount": 1},
            "$set": {
                "mostCommonResponse": most_common,
                "mostCommonResponseRank": rank,
                "lastContactDate": entry_data["timestamp"]
            }
        }
    )
    
    updated_lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
    return serialize_doc(updated_lead)

@api_router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str, request: Request):
    await require_admin(request)
    
    result = await db.leads.delete_one({"_id": ObjectId(lead_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {"message": "Lead deleted"}

# ============== DASHBOARD STATS ==============

@api_router.get("/stats/dashboard")
async def get_dashboard_stats(request: Request):
    user = await get_current_user(request)
    
    base_query = {}
    if user["role"] == "team_member":
        base_query["assignedTo"] = user["id"]
    
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    week_end = today + timedelta(days=7)
    
    # Pipeline stages breakdown
    pipeline_stats = []
    for stage in PIPELINE_STAGES:
        count = await db.leads.count_documents({**base_query, "pipelineStage": stage})
        pipeline_stats.append({"stage": stage, "count": count})
    
    # Category breakdown
    category_stats = []
    for cat, rank in CATEGORY_RANK.items():
        count = await db.leads.count_documents({**base_query, "category": cat})
        category_stats.append({"category": cat, "count": count, "rank": rank})
    
    # Priority breakdown
    priority_stats = []
    for pri, rank in PRIORITY_RANK.items():
        count = await db.leads.count_documents({**base_query, "priority": pri})
        priority_stats.append({"priority": pri, "count": count, "rank": rank})
    
    stats = {
        "totalLeads": await db.leads.count_documents(base_query),
        "todayFollowups": await db.leads.count_documents({**base_query, "nextFollowupDate": {"$gte": today.isoformat(), "$lt": tomorrow.isoformat()}}),
        "tomorrowFollowups": await db.leads.count_documents({**base_query, "nextFollowupDate": {"$gte": tomorrow.isoformat(), "$lt": (tomorrow + timedelta(days=1)).isoformat()}}),
        "weekFollowups": await db.leads.count_documents({**base_query, "nextFollowupDate": {"$gte": today.isoformat(), "$lt": week_end.isoformat()}}),
        "interestedLeads": await db.leads.count_documents({**base_query, "category": "Interested"}),
        "meetingsDone": await db.leads.count_documents({**base_query, "category": "Meeting Done"}),
        "pipelineStats": pipeline_stats,
        "categoryStats": category_stats,
        "priorityStats": priority_stats,
        "teamMembers": await db.users.count_documents({})
    }
    
    return stats

# ============== STARTUP ==============

@app.on_event("startup")
async def startup_db():
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.leads.create_index("category")
    await db.leads.create_index("priority")
    await db.leads.create_index("pipelineStage")
    await db.leads.create_index("assignedTo")
    await db.leads.create_index("nextFollowupDate")
    await db.leads.create_index([("categoryRank", 1), ("priorityRank", 1)])
    
    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@wedus.com").lower()
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    
    existing_admin = await db.users.find_one({"email": admin_email})
    if not existing_admin:
        await db.users.insert_one({
            "email": admin_email,
            "password_hash": hash_password(admin_password),
            "name": "Admin",
            "role": "admin",
            "color": "#E8536A",
            "created_at": datetime.now(timezone.utc)
        })
        logger.info(f"Admin user created: {admin_email}")
    elif not verify_password(admin_password, existing_admin["password_hash"]):
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": hash_password(admin_password)}}
        )
        logger.info(f"Admin password updated")
    
    # Seed sample team members
    sample_team = [
        {"name": "Priya Sharma", "email": "priya@wedus.com", "color": "#3B82F6"},
        {"name": "Rahul Mehta", "email": "rahul@wedus.com", "color": "#10B981"},
        {"name": "Ananya Singh", "email": "ananya@wedus.com", "color": "#F59E0B"}
    ]
    
    for member in sample_team:
        existing = await db.users.find_one({"email": member["email"]})
        if not existing:
            await db.users.insert_one({
                "email": member["email"],
                "password_hash": hash_password("team123"),
                "name": member["name"],
                "role": "team_member",
                "color": member["color"],
                "created_at": datetime.now(timezone.utc)
            })
            logger.info(f"Team member created: {member['email']}")
    
    # Write test credentials
    Path("/app/memory").mkdir(parents=True, exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write("# Wed Us CRM Test Credentials\n\n")
        f.write("## Admin Account\n")
        f.write(f"- Email: {admin_email}\n")
        f.write(f"- Password: {admin_password}\n")
        f.write("- Role: admin\n\n")
        f.write("## Team Members\n")
        for member in sample_team:
            f.write(f"- Email: {member['email']}\n")
            f.write("- Password: team123\n")
            f.write("- Role: team_member\n\n")
        f.write("## Auth Endpoints\n")
        f.write("- POST /api/auth/login\n")
        f.write("- POST /api/auth/logout\n")
        f.write("- GET /api/auth/me\n")
        f.write("- POST /api/auth/refresh\n")
    
    logger.info("Database initialized successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "Wed Us CRM API", "version": "1.0.0"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000"), "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
