from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime
import qrcode
from PIL import Image
import io
import base64


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class QRCodeRequest(BaseModel):
    text: str
    size: int = 10
    border: int = 4

class QRCodeResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    image_base64: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Add your routes to the router instead of directly to app
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

@api_router.post("/qr/generate", response_model=QRCodeResponse)
async def generate_qr_code(request: QRCodeRequest):
    try:
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=request.size,
            border=request.border,
        )
        qr.add_data(request.text)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Save to database
        qr_data = {
            "id": str(uuid.uuid4()),
            "text": request.text,
            "image_base64": img_str,
            "timestamp": datetime.utcnow()
        }
        await db.qr_codes.insert_one(qr_data)
        
        return QRCodeResponse(**qr_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")

@api_router.get("/qr/download/{qr_id}")
async def download_qr_code(qr_id: str):
    try:
        # Find QR code in database
        qr_data = await db.qr_codes.find_one({"id": qr_id})
        if not qr_data:
            raise HTTPException(status_code=404, detail="QR code not found")
        
        # Convert base64 to image
        img_data = base64.b64decode(qr_data["image_base64"])
        img = Image.open(io.BytesIO(img_data))
        
        # Convert to JPEG
        output = io.BytesIO()
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        img.save(output, format="JPEG", quality=95)
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="image/jpeg",
            headers={"Content-Disposition": f"attachment; filename=qr_code_{qr_id}.jpg"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading QR code: {str(e)}")

@api_router.get("/qr/list", response_model=List[QRCodeResponse])
async def get_qr_codes():
    try:
        qr_codes = await db.qr_codes.find().to_list(1000)
        return [QRCodeResponse(**qr_code) for qr_code in qr_codes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching QR codes: {str(e)}")

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
