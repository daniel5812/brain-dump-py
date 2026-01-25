"""
endpoints/user_onboarding.py - User Verification & Registration Routes

RESPONSIBILITIES:
- Handle /verify-user
- Handle /register (Serve HTML)
- Handle /register/complete

AUTHORITY:
- Uses crud.user_details for logic
- Uses static files for HTML
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os

from crud.user_details import verify_user, register_user
from tools.google_calendar.calendar_client import calendar_client

router = APIRouter()

# -----------------------------------------------------------------------------
# SCHEMAS (Local or imported, keeping it simple as requested)
# -----------------------------------------------------------------------------

class VerifyUserRequest(BaseModel):
    user_id: str

class VerifyUserResponse(BaseModel):
    status: str
    phone: str = None

class RegisterCompleteRequest(BaseModel):
    user_id: str
    phone: str
    email: str
    calendar_enabled: bool

class RegisterCompleteResponse(BaseModel):
    status: str

@router.get("/verify-user", response_model=VerifyUserResponse)
@router.post("/verify-user", response_model=VerifyUserResponse)
async def verify_user_endpoint(request: Request = None, data: VerifyUserRequest = None):
    """
    Checks if a device is registered and returns the associated phone number.
    Supports both GET (with query param) and POST (with body).
    """
    # Try to get device_id from POST body or GET query param
    device_id = None
    if data:
        device_id = data.user_id
    elif request:
        device_id = request.query_params.get("user_id")

    if not device_id:
        return VerifyUserResponse(status="MISSING_ID")

    from crud.user_details import get_user_by_device
    user = get_user_by_device(device_id)
    
    if user and user.get("calendar_enabled"):
        return VerifyUserResponse(
            status="OK",
            phone=user["user_id"] # The phone number is our primary user_id
        )
    
    return VerifyUserResponse(status="NEEDS_REGISTRATION")


@router.get("/register", response_class=HTMLResponse)
async def get_register_page():
    """
    GET /register
    Serves the registration HTML page.
    """
    # Assuming execution from backend/ root or consistent path
    # We'll use absolute path logic to find static/register.html
    
    current_dir = os.path.dirname(os.path.abspath(__file__)) # endpoints/
    backend_dir = os.path.dirname(current_dir) # backend/
    static_file = os.path.join(backend_dir, "static", "register.html")
    
    if os.path.exists(static_file):
        with open(static_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="<h1>Error: Register page not found</h1>", status_code=404)


@router.post("/register", response_model=RegisterCompleteResponse)
async def complete_registration(request: RegisterCompleteRequest):
    """
    POST /register
    Saves the mapping between technical user_id and manual phone/email.
    """
    # 1. Verify real access to the calendar
    has_access = calendar_client.verify_access(request.email)
    
    if not has_access:
        print(f"[onboarding] Verification FAILED for {request.email}")
        raise HTTPException(
            status_code=403, 
            detail=f"We couldn't access the calendar for {request.email}. "
                   f"Please make sure you shared it correctly with the agent email."
        )

    # 2. Save user data (mapping technical ID to phone/email)
    user_data = {
        "user_id": request.user_id, # Technical ID from Shortcut
        "phone": request.phone,     # Manual Phone from HTML
        "email": request.email,     # Manual Email from HTML
        "calendar_enabled": request.calendar_enabled
    }
    
    register_user(user_data)
    
    print(f"[onboarding] User {request.user_id} registered with phone {request.phone}")
    return RegisterCompleteResponse(status="OK")
