from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt
import qrcode
import io
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-here')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="TimeTracker Pro API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# === MODELS ===

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    type: str  # 'owner', 'admin', 'user'
    role: str  # same as type for compatibility
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    password: str
    type: str
    company_id: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    type: Optional[str] = None
    company_id: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    type: str
    role: str
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    created_at: datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CompanyCreate(BaseModel):
    name: str

class CompanyUpdate(BaseModel):
    name: Optional[str] = None

class Employee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    qr_code: str
    company_id: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmployeeCreate(BaseModel):
    name: str
    company_id: str

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class TimeEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    check_in: datetime
    check_out: Optional[datetime] = None
    date: str
    total_hours: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TimeEntryCreate(BaseModel):
    employee_id: str
    check_in: datetime
    check_out: Optional[datetime] = None

class TimeEntryUpdate(BaseModel):
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class QRResponse(BaseModel):
    qr_code_data: str
    qr_code_image: str  # base64 encoded image

# === UTILITY FUNCTIONS ===

def hash_password(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(token_payload: dict = Depends(verify_token)) -> dict:
    """Get current user from token"""
    user_id = token_payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

def generate_qr_code(data: str) -> str:
    """Generate QR code and return base64 encoded image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_str = base64.b64encode(buf.getvalue()).decode()
    return img_str

# === INITIALIZATION ===

async def init_default_data():
    """Initialize default data if not exists"""
    # Check if owner exists
    owner = await db.users.find_one({"username": "owner"})
    if not owner:
        # Create default users
        default_users = [
            {
                "id": str(uuid.uuid4()),
                "username": "owner",
                "password_hash": hash_password("owner123"),
                "type": "owner",
                "role": "owner",
                "company_id": None,
                "company_name": "System Owner",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "password_hash": hash_password("admin123"),
                "type": "admin",
                "role": "admin",
                "company_id": "1",
                "company_name": "Firma ABC",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "username": "user",
                "password_hash": hash_password("user123"),
                "type": "user",
                "role": "user",
                "company_id": "1",
                "company_name": "Firma ABC",
                "created_at": datetime.utcnow()
            }
        ]
        await db.users.insert_many(default_users)
        
        # Create default companies
        default_companies = [
            {
                "id": "1",
                "name": "Firma ABC",
                "created_at": datetime.utcnow()
            },
            {
                "id": "2",
                "name": "Firma XYZ",
                "created_at": datetime.utcnow()
            }
        ]
        await db.companies.insert_many(default_companies)
        
        # Create default employees
        default_employees = [
            {
                "id": "1",
                "name": "Jan Kowalski",
                "qr_code": "QR-EMP-001",
                "company_id": "1",
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "id": "2",
                "name": "Anna Nowak",
                "qr_code": "QR-EMP-002",
                "company_id": "1",
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        ]
        await db.employees.insert_many(default_employees)
        
        # Create default time entries
        default_time_entries = [
            {
                "id": "1",
                "employee_id": "1",
                "check_in": datetime.utcnow().replace(hour=8, minute=0, second=0),
                "check_out": datetime.utcnow().replace(hour=16, minute=0, second=0),
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "total_hours": 8.0,
                "created_at": datetime.utcnow()
            },
            {
                "id": "2",
                "employee_id": "2",
                "check_in": datetime.utcnow().replace(hour=9, minute=0, second=0),
                "check_out": datetime.utcnow().replace(hour=17, minute=0, second=0),
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "total_hours": 8.0,
                "created_at": datetime.utcnow()
            }
        ]
        await db.time_entries.insert_many(default_time_entries)

# === AUTHENTICATION ROUTES ===

@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login"""
    user = await db.users.find_one({"username": request.username})
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token({"user_id": user["id"]})
    
    # Get company name if user belongs to a company
    company_name = user.get("company_name")
    if user.get("company_id"):
        company = await db.companies.find_one({"id": user["company_id"]})
        if company:
            company_name = company["name"]
    
    user_response = UserResponse(
        id=user["id"],
        username=user["username"],
        type=user["type"],
        role=user["role"],
        company_id=user.get("company_id"),
        company_name=company_name,
        created_at=user["created_at"]
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

# === COMPANY ROUTES ===

@api_router.get("/companies", response_model=List[Company])
async def get_companies(current_user: dict = Depends(get_current_user)):
    """Get all companies (owner only)"""
    if current_user["type"] != "owner":
        raise HTTPException(status_code=403, detail="Access denied")
    
    companies = await db.companies.find().to_list(1000)
    return companies

@api_router.post("/companies", response_model=Company)
async def create_company(company: CompanyCreate, current_user: dict = Depends(get_current_user)):
    """Create new company (owner only)"""
    if current_user["type"] != "owner":
        raise HTTPException(status_code=403, detail="Access denied")
    
    company_obj = Company(**company.dict())
    await db.companies.insert_one(company_obj.dict())
    return company_obj

@api_router.put("/companies/{company_id}", response_model=Company)
async def update_company(company_id: str, company: CompanyUpdate, current_user: dict = Depends(get_current_user)):
    """Update company (owner only)"""
    if current_user["type"] != "owner":
        raise HTTPException(status_code=403, detail="Access denied")
    
    existing_company = await db.companies.find_one({"id": company_id})
    if not existing_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_data = {k: v for k, v in company.dict().items() if v is not None}
    if update_data:
        await db.companies.update_one({"id": company_id}, {"$set": update_data})
    
    updated_company = await db.companies.find_one({"id": company_id})
    return updated_company

@api_router.delete("/companies/{company_id}")
async def delete_company(company_id: str, current_user: dict = Depends(get_current_user)):
    """Delete company (owner only)"""
    if current_user["type"] != "owner":
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.companies.delete_one({"id": company_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return {"message": "Company deleted successfully"}

# === USER ROUTES ===

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get users (owner: all users, admin: users from their company)"""
    if current_user["type"] == "owner":
        users = await db.users.find().to_list(1000)
    elif current_user["type"] == "admin":
        # Admin can only see users from their company
        users = await db.users.find({"company_id": current_user["company_id"]}).to_list(1000)
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user_responses = []
    for user in users:
        company_name = user.get("company_name")
        if user.get("company_id"):
            company = await db.companies.find_one({"id": user["company_id"]})
            if company:
                company_name = company["name"]
        
        user_responses.append(UserResponse(
            id=user["id"],
            username=user["username"],
            type=user["type"],
            role=user["role"],
            company_id=user.get("company_id"),
            company_name=company_name,
            created_at=user["created_at"]
        ))
    
    return user_responses

@api_router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    """Create new user (owner: any user, admin: users for their company only)"""
    if current_user["type"] == "owner":
        # Owner can create users for any company
        pass
    elif current_user["type"] == "admin":
        # Admin can only create users for their company
        if not user.company_id:
            user.company_id = current_user["company_id"]
        elif user.company_id != current_user["company_id"]:
            raise HTTPException(status_code=403, detail="Cannot create users for other companies")
        # Admin cannot create owner accounts
        if user.type == "owner":
            raise HTTPException(status_code=403, detail="Cannot create owner accounts")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if username already exists
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Get company name if provided
    company_name = None
    if user.company_id:
        company = await db.companies.find_one({"id": user.company_id})
        if company:
            company_name = company["name"]
    
    user_obj = User(
        username=user.username,
        password_hash=hash_password(user.password),
        type=user.type,
        role=user.type,
        company_id=user.company_id,
        company_name=company_name
    )
    
    await db.users.insert_one(user_obj.dict())
    
    return UserResponse(
        id=user_obj.id,
        username=user_obj.username,
        type=user_obj.type,
        role=user_obj.role,
        company_id=user_obj.company_id,
        company_name=company_name,
        created_at=user_obj.created_at
    )

@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Update user (owner: any user, admin: users from their company only)"""
    existing_user = await db.users.find_one({"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user["type"] == "owner":
        # Owner can update any user
        pass
    elif current_user["type"] == "admin":
        # Admin can only update users from their company
        if existing_user.get("company_id") != current_user["company_id"]:
            raise HTTPException(status_code=403, detail="Cannot update users from other companies")
        # Admin cannot change user type to owner
        if user.type == "owner":
            raise HTTPException(status_code=403, detail="Cannot create owner accounts")
        # Admin cannot update owner accounts
        if existing_user.get("type") == "owner":
            raise HTTPException(status_code=403, detail="Cannot update owner accounts")
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = {k: v for k, v in user.dict().items() if v is not None}
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    if "type" in update_data:
        update_data["role"] = update_data["type"]
    
    # Get company name if company_id is being updated
    if "company_id" in update_data:
        if current_user["type"] == "admin" and update_data["company_id"] != current_user["company_id"]:
            raise HTTPException(status_code=403, detail="Cannot assign users to other companies")
        company = await db.companies.find_one({"id": update_data["company_id"]})
        if company:
            update_data["company_name"] = company["name"]
    
    if update_data:
        await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"id": user_id})
    return UserResponse(
        id=updated_user["id"],
        username=updated_user["username"],
        type=updated_user["type"],
        role=updated_user["role"],
        company_id=updated_user.get("company_id"),
        company_name=updated_user.get("company_name"),
        created_at=updated_user["created_at"]
    )

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Delete user (owner only)"""
    if current_user["type"] != "owner":
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

# === EMPLOYEE ROUTES ===

@api_router.get("/employees", response_model=List[Employee])
async def get_employees(current_user: dict = Depends(get_current_user)):
    """Get employees (admin/user for their company, owner for all)"""
    if current_user["type"] == "owner":
        employees = await db.employees.find().to_list(1000)
    else:
        employees = await db.employees.find({"company_id": current_user["company_id"]}).to_list(1000)
    
    return employees

@api_router.post("/employees", response_model=Employee)
async def create_employee(employee: EmployeeCreate, current_user: dict = Depends(get_current_user)):
    """Create new employee (admin only)"""
    if current_user["type"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Generate QR code
    qr_code = f"QR-EMP-{str(uuid.uuid4())[:8].upper()}"
    
    employee_obj = Employee(
        name=employee.name,
        qr_code=qr_code,
        company_id=employee.company_id
    )
    
    await db.employees.insert_one(employee_obj.dict())
    return employee_obj

@api_router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: str, employee: EmployeeUpdate, current_user: dict = Depends(get_current_user)):
    """Update employee (admin only)"""
    if current_user["type"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    existing_employee = await db.employees.find_one({"id": employee_id})
    if not existing_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    update_data = {k: v for k, v in employee.dict().items() if v is not None}
    if update_data:
        await db.employees.update_one({"id": employee_id}, {"$set": update_data})
    
    updated_employee = await db.employees.find_one({"id": employee_id})
    return updated_employee

@api_router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str, current_user: dict = Depends(get_current_user)):
    """Delete employee (admin only)"""
    if current_user["type"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.employees.delete_one({"id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {"message": "Employee deleted successfully"}

@api_router.post("/employees/{employee_id}/qr", response_model=QRResponse)
async def generate_employee_qr(employee_id: str, current_user: dict = Depends(get_current_user)):
    """Generate QR code for employee (admin only)"""
    if current_user["type"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    employee = await db.employees.find_one({"id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    qr_image = generate_qr_code(employee["qr_code"])
    
    return QRResponse(
        qr_code_data=employee["qr_code"],
        qr_code_image=qr_image
    )

# === TIME ENTRY ROUTES ===

@api_router.get("/time-entries", response_model=List[TimeEntry])
async def get_time_entries(current_user: dict = Depends(get_current_user)):
    """Get time entries (admin/user for their company, owner for all)"""
    if current_user["type"] == "owner":
        time_entries = await db.time_entries.find().to_list(1000)
    else:
        # Get employees from user's company first
        employees = await db.employees.find({"company_id": current_user["company_id"]}).to_list(1000)
        employee_ids = [emp["id"] for emp in employees]
        time_entries = await db.time_entries.find({"employee_id": {"$in": employee_ids}}).to_list(1000)
    
    return time_entries

@api_router.post("/time-entries", response_model=TimeEntry)
async def create_time_entry(time_entry: TimeEntryCreate, current_user: dict = Depends(get_current_user)):
    """Create new time entry"""
    employee = await db.employees.find_one({"id": time_entry.employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Calculate total hours if check_out is provided
    total_hours = None
    if time_entry.check_out:
        delta = time_entry.check_out - time_entry.check_in
        total_hours = delta.total_seconds() / 3600
    
    time_entry_obj = TimeEntry(
        employee_id=time_entry.employee_id,
        check_in=time_entry.check_in,
        check_out=time_entry.check_out,
        date=time_entry.check_in.strftime("%Y-%m-%d"),
        total_hours=total_hours
    )
    
    await db.time_entries.insert_one(time_entry_obj.dict())
    return time_entry_obj

@api_router.put("/time-entries/{entry_id}", response_model=TimeEntry)
async def update_time_entry(entry_id: str, time_entry: TimeEntryUpdate, current_user: dict = Depends(get_current_user)):
    """Update time entry (admin only)"""
    if current_user["type"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    existing_entry = await db.time_entries.find_one({"id": entry_id})
    if not existing_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    update_data = {k: v for k, v in time_entry.dict().items() if v is not None}
    
    # Recalculate total hours if check_in or check_out is updated
    if "check_in" in update_data or "check_out" in update_data:
        check_in = update_data.get("check_in", existing_entry["check_in"])
        check_out = update_data.get("check_out", existing_entry.get("check_out"))
        
        if check_in and check_out:
            delta = check_out - check_in
            update_data["total_hours"] = delta.total_seconds() / 3600
    
    if update_data:
        await db.time_entries.update_one({"id": entry_id}, {"$set": update_data})
    
    updated_entry = await db.time_entries.find_one({"id": entry_id})
    return updated_entry

@api_router.delete("/time-entries/{entry_id}")
async def delete_time_entry(entry_id: str, current_user: dict = Depends(get_current_user)):
    """Delete time entry (admin only)"""
    if current_user["type"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.time_entries.delete_one({"id": entry_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    return {"message": "Time entry deleted successfully"}

# === ORIGINAL ROUTES (for compatibility) ===

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

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await init_default_data()
    logger.info("Application started and default data initialized")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
